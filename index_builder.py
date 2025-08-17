from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from config import OPENAI_API_KEY
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

def build_index(documents, persist_dir="./storage"):
    Settings.llm = OpenAI(api_key = OPENAI_API_KEY)
    Settings.embed_model = OpenAIEmbedding(api_key = OPENAI_API_KEY)

    print("No index found — building from documents")
    splitter = SentenceSplitter(chunk_size = 1000, chunk_overlap = 150)
    nodes = splitter.get_nodes_from_documents(documents)
    index = VectorStoreIndex(nodes)
    #index = VectorStoreIndex.from_documents(documents) # <- shorthand with chunking defaults

    index.storage_context.persist(persist_dir = persist_dir)

    return index
