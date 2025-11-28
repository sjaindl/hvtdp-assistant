# example_run.py
import asyncio

from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import HierarchicalNodeParser

from eval.eval_utils import run_retrieval_eval, EvalItem, debug_automerge
from ingest.docs_reader import load_local_docs
from ingest.endpoint_spec import fullSpecs
from ingest.rest_api_reader import load_api_endpoints
from ingest.webpage_scraper import load_web_docs


def test():

    # 1) Deine Documents (API + Web) laden/erzeugen …
    #documents = [...]  # List[Document], bereits mit metadata (z.B. important=True)
    documents = []
    documents += load_local_docs()
    documents += load_api_endpoints(fullSpecs)
    documents += asyncio.run(load_web_docs())

    # 2) Hierarchisch chunken, damit AutoMerging Parents kennt
    hnp = HierarchicalNodeParser.from_defaults(chunk_sizes=[400, 1200, 2400])
    nodes = hnp.get_nodes_from_documents(documents)

    # 3) Index bauen (über LEAF/alle zurückgegebenen Nodes)
    index = VectorStoreIndex(nodes)

    # 4) Eval-Set definieren
    EVAL = [
        EvalItem(
            query="Welche Spieler sind im Kader vom HV TDP?",
            relevant_ref_doc_ids={"API_KADER_REF_DOC_ID"}  # <- setze hier deine echte(n) ref_doc_id(s)
        ),
        # Weitere Queries …
    ]

    # 5) Evaluieren
    rows = run_retrieval_eval(
        index=index,
        eval_items=EVAL,
        all_nodes=nodes,
        top_k_metric=12,
        similarity_top_k=40,   # breit holen
        mmr=True,              # Vielfalt
        automerge=True,        # Parent hochziehen
        automerge_ratio=0.5,   # ab 50% Kinder -> Parent
        use_reranker=True,     # lokaler Cross-Encoder
        rerank_top_n=12,
        use_boost=True,        # falls du important=True boostest
        boost_bonus=0.12,
    )
    print("\n=== Retrieval Eval (Hit@12 / MRR@12) ===")
    for name, hit, mrr in rows:
        print(f"{name:35s}  Hit@12={hit:.3f}  MRR@12={mrr:.3f}")

    # 6) AutoMerging debuggen
    from llama_index.core.retrievers import VectorIndexRetriever, AutoMergingRetriever

    vec_ret = VectorIndexRetriever(index=index, similarity_top_k=40, vector_store_query_mode="mmr")
    am_ret = AutoMergingRetriever(vector_retriever=vec_ret, storage_context=index.storage_context, simple_ratio_thresh=0.5)

    # optional: Postprozessoren in der Debug-Sicht weglassen, um das reine Merging zu sehen
    debug_automerge(
        query="Welche Spieler sind im Kader vom HV TDP?",
        retriever=am_ret,
        storage_context=index.storage_context,
        all_nodes=nodes,
        top_k=12,
    )
