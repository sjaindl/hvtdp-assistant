import os

from llama_index.core import VectorStoreIndex, load_index_from_storage, StorageContext
from config import OPENAI_API_KEY
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

def build_or_load_index(documents, persist_dir="./storage"):
    Settings.llm = OpenAI(api_key = OPENAI_API_KEY)
    Settings.embed_model = OpenAIEmbedding(api_key = OPENAI_API_KEY)

    if os.path.exists(persist_dir) and os.path.exists(os.path.join(persist_dir, "index_store.json")):
        print("Index found — loading from storage")
        storage_context = StorageContext.from_defaults(persist_dir = persist_dir)
        index = load_index_from_storage(storage_context)
    else:
        print("No index found — building from documents")
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir = persist_dir)

    return index
