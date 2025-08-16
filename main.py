#from ingest.ingest_sql import load_sql_docs
#from ingest.ingest_web import load_web_docs
#from ingest.ingest_docs import load_local_docs
#from ingest.ingest_github import load_github_docs
import os

from index_builder import build_index
from index_loader import load_index
from chat_engine import build_chat_engine
from ingest.docs_reader import load_local_docs
from ingest.rest_api_reader import load_api_endpoints, specs

def ingest_all():
    docs = []
    docs += load_local_docs()
    docs += load_api_endpoints(specs)
    #docs += load_sql_docs()
    #docs += load_web_docs()
    #docs += load_github_docs()
    return docs

if __name__ == "__main__":
    if not os.path.exists("./storage") and not os.path.exists(os.path.join("./storage", "index_store.json")):
        print("Ingesting data...")
        documents = ingest_all()
        index = build_index(documents)
    else:
        index = load_index()

    print("Chatbot ready. Ask your question:")
    engine = build_chat_engine(index)

    while True:
        q = input("\nYou: ")
        if q.lower() in {"exit", "quit"}:
            break
        response = engine.chat(q)
        print("\nHV TDP Assistant:", response)
