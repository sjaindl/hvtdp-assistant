from __future__ import annotations

import logging
import os
import sys

from config import QDRANT_API_KEY, OPENAI_API_KEY, USE_TOOL_ENGINE, QDRANT_URL
from engine.chat_engine import build_chat_engine
from engine.tooling_engine import wrap_rag_as_tool, build_router_chat_with_tools
from eval.llama_eval import eval_faithfulness
from indexing.index_builder import build_index
from indexing.index_loader import load_index
from ingest.ingest_base import ingest_all
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from qdrant_client import QdrantClient

logging.basicConfig(stream = sys.stdout, level = logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream = sys.stdout))

eval_mode = False

if __name__ == "__main__":
    Settings.embed_model = HuggingFaceEmbedding(
        model_name = "BAAI/bge-m3",  # 1024-dim
        #model_name="intfloat/multilingual-e5-small",  # ~120MB, 384-dim
        device="cpu",
    )

    Settings.llm = OpenAI(api_key = OPENAI_API_KEY)
    Settings.embed_model = OpenAIEmbedding(api_key = OPENAI_API_KEY)

    if not os.path.exists("./storage") and not os.path.exists(os.path.join("./storage", "index_store.json")):
        print("Ingesting data")
        documents = ingest_all()
        index = build_index(documents)
    else:
        index = load_index()

    qdrant_client = QdrantClient(
        url = QDRANT_URL,
        api_key = QDRANT_API_KEY,
    )

    if eval_mode:
        engine = build_chat_engine(index)
        eval_faithfulness(index)
    else:
        print("Chatbot ready. Ask your question:")

        if USE_TOOL_ENGINE:
            rag_tool = wrap_rag_as_tool(index)
            engine, tools = build_router_chat_with_tools(extra_tools=[rag_tool])
        else:
            engine = build_chat_engine(index)

        while True:
            query = input("\nYou: ")
            if query.lower() in {"exit", "quit"}:
                break

            response = engine.chat(query)
            print("\nHV TDP Assistant:", response)
