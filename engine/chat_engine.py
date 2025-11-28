from config import TOKEN_LIMIT
from engine.postprocessor import BoostImportant
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.vector_stores.types import VectorStoreQueryMode

def build_chat_engine(
        index: VectorStoreIndex,
        token_limit: int = TOKEN_LIMIT,
):
    return CondenseQuestionChatEngine.from_defaults(
        query_engine = build_optimized_query_engine(index),
        memory = ChatMemoryBuffer.from_defaults(token_limit = token_limit),
    )

def build_optimized_query_engine(
        index: VectorStoreIndex,
):
    post = BoostImportant(bonus = 0.12)

    reranker = SentenceTransformerRerank(
        model = "jinaai/jina-reranker-v2-base-multilingual",
        #model = "BAAI/bge-reranker-v2-m3", # multilingual
        #model = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n = 12, # context cutoff
        device = "cpu",
    )

    vec_retriever = VectorIndexRetriever(index, similarity_top_k = 40, vector_store_query_mode = VectorStoreQueryMode.HYBRID, sparse_top_k = 40)

    retriever = AutoMergingRetriever(
        vector_retriever = vec_retriever,
        storage_context = index.storage_context,
        simple_ratio_thresh = 0.5,
    )

    synth = get_response_synthesizer(response_mode = ResponseMode.REFINE)

    return RetrieverQueryEngine(
        retriever = retriever,
        node_postprocessors = [reranker, post],
        response_synthesizer = synth,
    )
