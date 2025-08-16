from llama_index.core import VectorStoreIndex
from config import OPENAI_API_KEY
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

def build_index(documents, persist_dir="./storage"):
    Settings.llm = OpenAI(api_key = OPENAI_API_KEY)
    Settings.embed_model = OpenAIEmbedding(api_key = OPENAI_API_KEY)

    print("No index found — building from documents")
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir = persist_dir)

    return index
