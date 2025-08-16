#from ingest.ingest_sql import load_sql_docs
#from ingest.ingest_web import load_web_docs
#from ingest.ingest_docs import load_local_docs
#from ingest.ingest_github import load_github_docs
from ingest.docs_reader import load_csv

from index_builder import build_or_load_index
from query_engine import get_query_engine
from ingest.docs_reader import load_local_docs

def ingest_all():
    docs = []
    docs += load_local_docs()
    #docs += load_sql_docs()
    #docs += load_web_docs()
    #docs += load_github_docs()
    return docs

if __name__ == "__main__":
    print("Ingesting data...")
    documents = ingest_all()

    print("Building index...")
    build_or_load_index(documents)

    print("Chatbot ready. Ask your question:")
    engine = get_query_engine()

    while True:
        q = input("\nYou: ")
        if q.lower() in {"exit", "quit"}:
            break
        response = engine.query(q)
        print("\nHV TDP Assistant:", response)
