import asyncio

from ingest.docs_reader import load_local_docs
from ingest.endpoint_spec import newsSpec
from ingest.rest_api_reader import load_api_endpoints
from ingest.webpage_scraper import load_web_docs

def ingest_all():
    docs = []

    docs += load_local_docs()

    # can be switched to fullSpecs, however, other specs are currently handled via tooling
    docs += load_api_endpoints([newsSpec])

    docs += asyncio.run(load_web_docs())

    return docs
