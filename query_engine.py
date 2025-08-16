from config import OPENAI_API_KEY
from llama_index.core.settings import Settings

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

def get_query_engine():
    Settings.llm = OpenAI(api_key=OPENAI_API_KEY)
    Settings.embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)

    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    index = load_index_from_storage(storage_context)
    return index.as_query_engine()
