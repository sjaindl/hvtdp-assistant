from config import CHUNK_SIZE, CHUNK_OVERLAP
from indexing.vector_store import build_vector_store
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter

def build_index(documents, persist_dir="./storage"):
    print("No index found — building from documents")

    vector_store = build_vector_store()

    splitter = SentenceSplitter(chunk_size = CHUNK_SIZE, chunk_overlap = CHUNK_OVERLAP, separator="\n\n")
    nodes = splitter.get_nodes_from_documents(documents)

    # persist docstore locally (vectors go to Qdrant)
    storage = StorageContext.from_defaults(vector_store = vector_store)
    index = VectorStoreIndex(nodes, storage_context = storage)
    index.storage_context.persist(persist_dir = persist_dir)

    return index
