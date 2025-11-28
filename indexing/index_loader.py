from indexing.vector_store import build_vector_store
from llama_index.core import load_index_from_storage, StorageContext

def load_index(persist_dir="./storage"):
    print("Index found — loading from storage")

    vector_store = build_vector_store()

    storage_context = StorageContext.from_defaults(
        persist_dir = persist_dir,
        vector_store = vector_store,
    )

    # loading the index metadata & docstore (vectors are in Qdrant)
    index = load_index_from_storage(storage_context)

    return index
