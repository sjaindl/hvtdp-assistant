from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from config import OPENAI_API_KEY, QDRANT_API_KEY, QDRANT_URL
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

def build_vector_store():
    Settings.llm = OpenAI(api_key = OPENAI_API_KEY)
    Settings.embed_model = OpenAIEmbedding(api_key = OPENAI_API_KEY)

    qdrant_client = QdrantClient(
        url = QDRANT_URL,
        api_key = QDRANT_API_KEY,
    )

    return QdrantVectorStore(
        client = qdrant_client,
        collection_name = "hvtdp_docs_optimized",
        enable_hybrid = True,
        dense_vector_name = "dense-vector",
        sparse_vector_name = "sparse-vector",
        batch_size = 64,
    )
