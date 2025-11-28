from llama_index.core import StorageContext, load_index_from_storage

def basic_query_engine():
    storage_context = StorageContext.from_defaults(persist_dir="../storage")
    index = load_index_from_storage(storage_context)

    return index.as_query_engine()
