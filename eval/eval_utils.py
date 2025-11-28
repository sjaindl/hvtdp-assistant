# eval_utils.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Set, Dict, Tuple, Optional
from collections import defaultdict

# LlamaIndex
from llama_index.core import VectorStoreIndex
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, TextNode, QueryBundle, NodeRelationship
from llama_index.core.retrievers import VectorIndexRetriever, AutoMergingRetriever, BaseRetriever
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.vector_stores.types import VectorStoreQueryMode

from engine.postprocessor import BoostImportant


# -----------------------------
# Eval-Datentyp
# -----------------------------
@dataclass
class EvalItem:
    query: str
    # Ground Truth: welche ref_doc_id(s) sind "richtig"?
    relevant_ref_doc_ids: Set[str]

# -----------------------------
# Boost-Postprozessor (optional)
# -----------------------------
# class BoostImportant(BaseNodePostprocessor):
#     def __init__(self, bonus: float = 0.1, key: str = "important"):
#         self.bonus = bonus
#         self.key = key
#     def postprocess_nodes(self, nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle] = None, query_str: Optional[str] = None) -> List[NodeWithScore]:
#         for n in nodes:
#             if (n.node.metadata or {}).get(self.key) is True:
#                 n.score = (n.score or 0.0) + self.bonus
#         nodes.sort(key=lambda x: x.score or 0.0, reverse=True)
#         return nodes

# -----------------------------
# Hilfsfunktionen für Mappings
# -----------------------------
def build_nodes_by_refdoc(nodes: List[TextNode]) -> Dict[str, List[str]]:
    m: Dict[str, List[str]] = defaultdict(list)
    for nd in nodes:
        # Leaf- und evtl. Parent-Nodes haben eine ref_doc_id
        if nd.ref_doc_id:
            m[nd.ref_doc_id].append(nd.node_id)
    return m

def build_parent_children_maps(nodes: List[TextNode]) -> Tuple[Dict[str, Optional[str]], Dict[str, List[str]]]:
    """Gibt parent_of[node_id] und children_of[parent_id] zurück, basierend auf Node.relationships."""
    parent_of: Dict[str, Optional[str]] = {}
    children_of: Dict[str, List[str]] = defaultdict(list)
    for nd in nodes:
        pid = None
        # Relationship auslesen (robust gegen Versionsunterschiede)
        rel = getattr(nd, "relationships", None)
        if rel and isinstance(rel, dict):
            info = rel.get(NodeRelationship.PARENT)
            if info:
                pid = info.node_id
        parent_of[nd.node_id] = pid
        if pid:
            children_of[pid].append(nd.node_id)
    return parent_of, children_of

def parent_chain(node_id: str, storage_context) -> List[str]:
    """Liest über die Docstore die Parent-Kette hoch bis zur Wurzel."""
    chain = []
    ds = storage_context.docstore
    curr = node_id
    seen = set()
    while curr and curr not in seen:
        seen.add(curr)
        chain.append(curr)
        node: TextNode = ds.get_node(curr)
        rel = getattr(node, "relationships", None)
        pid = None
        if rel and isinstance(rel, dict):
            info = rel.get(NodeRelationship.PARENT)
            if info:
                pid = info.node_id
        curr = pid
    return chain  # [leaf, ..., top_parent]

# -----------------------------
# Reranker (lokal)
# -----------------------------
def make_local_reranker(model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", top_n: int = 12):
    return SentenceTransformerRerank(model=model, top_n=top_n)

# -----------------------------
# Primitive Eval-Metriken (lokal)
# -----------------------------
def eval_hit_mrr(
        retriever,
        items,
        nodes_by_refdoc,
        k: int = 12,
        postprocessors=None,
) -> Tuple[float, float]:
    hits, mrr_sum, n = 0, 0.0, len(items)
    for it in items:
        qb = QueryBundle(it.query)

        # 1) retrieve; be robust across versions (QueryBundle or plain str)
        try:
            res = retriever.retrieve(qb)
        except TypeError:
            res = retriever.retrieve(it.query)

        # 2) apply postprocessors (pass the QueryBundle!)
        for pp in (postprocessors or []):
            try:
                res = pp.postprocess_nodes(res, qb)
            except TypeError:
                # older postprocessors may not accept the bundle
                res = pp.postprocess_nodes(res)

        top = res[:k]

        # 3) evaluate
        gt_nodes = set().union(*(nodes_by_refdoc.get(did, []) for did in it.relevant_ref_doc_ids))
        ranks = [i + 1 for i, nw in enumerate(top) if nw.node.node_id in gt_nodes]
        if ranks:
            hits += 1
            mrr_sum += 1.0 / min(ranks)

    return (hits / n if n else 0.0), (mrr_sum / n if n else 0.0)

# -----------------------------
# Varianten bauen
# -----------------------------
@dataclass
class VariantConfig:
    name: str
    retriever: BaseRetriever
    postprocessors: List[BaseNodePostprocessor]

def build_variants_for_eval(
        index: VectorStoreIndex,
        *,
        similarity_top_k: int = 40,
        mmr: bool = True,
        automerge: bool = True,
        automerge_ratio: float = 0.5,
        use_reranker: bool = True,
        rerank_top_n: int = 12,
        use_boost: bool = False,
        boost_bonus: float = 0.1,
) -> List[VariantConfig]:
    # Baseline Vector Retriever
    vec_mode = VectorStoreQueryMode.MMR if mmr else VectorStoreQueryMode.DEFAULT
    base_vec = VectorIndexRetriever(
        index=index,
        similarity_top_k=similarity_top_k,
        vector_store_query_mode=vec_mode,
    )
    variants: List[VariantConfig] = []

    # (1) Baseline
    variants.append(VariantConfig(
        name=f"{vec_mode}@{similarity_top_k}",
        retriever=base_vec,
        postprocessors=[]
    ))

    # (2) +AutoMerging
    am = AutoMergingRetriever(
        vector_retriever=base_vec,
        storage_context=index.storage_context,
        simple_ratio_thresh=automerge_ratio,
    )

    if automerge:
        variants.append(VariantConfig(
            name=f"{vec_mode}+AM({automerge_ratio})",
            retriever=am,
            postprocessors=[]
        ))

    # (3) +Rerank (lokal)
    if use_reranker:
        reranker = make_local_reranker(top_n=rerank_top_n)
        variants.append(VariantConfig(
            name=f"{vec_mode}+Rerank@{rerank_top_n}",
            retriever=base_vec,
            postprocessors=[reranker]
        ))
        if automerge:
            variants.append(VariantConfig(
                name=f"{vec_mode}+AM({automerge_ratio})+Rerank@{rerank_top_n}",
                retriever=am,
                postprocessors=[reranker]
            ))

    # (4) optional: +Booster
    if use_boost:
        booster = BoostImportant(bonus=boost_bonus)
        variants = [
            VariantConfig(v.name + f"+Boost({boost_bonus})", v.retriever, v.postprocessors + [booster])
            for v in variants
        ]

    return variants

# -----------------------------
# Tabellarisches Ergebnis
# -----------------------------
def run_retrieval_eval(
        index: VectorStoreIndex,
        eval_items: List[EvalItem],
        all_nodes: List[TextNode],
        *,
        top_k_metric: int = 12,
        similarity_top_k: int = 40,
        mmr: bool = True,
        automerge: bool = True,
        automerge_ratio: float = 0.5,
        use_reranker: bool = True,
        rerank_top_n: int = 12,
        use_boost: bool = False,
        boost_bonus: float = 0.1,
) -> List[Tuple[str, float, float]]:
    nodes_by_refdoc = build_nodes_by_refdoc(all_nodes)
    variants = build_variants_for_eval(
        index,
        similarity_top_k=similarity_top_k,
        mmr=mmr,
        automerge=automerge,
        automerge_ratio=automerge_ratio,
        use_reranker=use_reranker,
        rerank_top_n=rerank_top_n,
        use_boost=use_boost,
        boost_bonus=boost_bonus,
    )
    rows = []
    for v in variants:
        hit, mrr = eval_hit_mrr(v.retriever, eval_items, nodes_by_refdoc, k=top_k_metric, postprocessors=v.postprocessors)
        rows.append((v.name, hit, mrr))
    return rows

# -----------------------------
# AutoMerging Debug / Inspection
# -----------------------------
def debug_automerge(
        query: str,
        retriever: BaseRetriever,
        storage_context,
        all_nodes: List[TextNode],
        top_k: int = 12,
) -> None:
    """
    Zeigt für die TOP-k Treffer:
    - node_id, ref_doc_id
    - Parent-Kette (leaf -> ... -> root) + Längen
    - Kurzer Textauszug
    """
    res: List[NodeWithScore] = retriever.retrieve(query)[:top_k]
    print(f"\n[DEBUG AutoMerging] Query: {query}")
    print(f"Top-{top_k} Treffer: {len(res)}")
    for i, nw in enumerate(res, 1):
        node: TextNode = nw.node
        chain = parent_chain(node.node_id, storage_context)
        ref = node.ref_doc_id
        snippet = (node.get_content() or "")[:140].replace("\n", " ")
        print(f"\n#{i} score={round(nw.score or 0.0, 4)} node={node.node_id} ref_doc={ref}")
        print(f"  parent_chain(len={len(chain)}): {' -> '.join(chain)}")
        print(f"  text: {snippet}...")

    # Optional: zeige, wie viele Kinder ein Parent hat (schneller Überblick)
    parent_of, children_of = build_parent_children_maps(all_nodes)
    print("\n[Parents mit #Children >= 2 (Ausschnitt)]")
    cnt = 0
    for pid, kids in children_of.items():
        if len(kids) >= 2:
            print(f"  parent={pid} children={len(kids)}")
            cnt += 1
            if cnt >= 10:
                break
