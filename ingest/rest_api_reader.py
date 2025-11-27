from typing import List
from llama_index.core import Document
from config import MAX_DOC_LEN
import requests

from ingest.api_utils import _build_description, _record_iter, _format_record_to_text
from ingest.endpoint_spec import EndpointSpec
from ingest.news_reader import build_news_records, news_record_to_document

def load_api_data(spec: EndpointSpec) -> List[Document]:
    """Load a single endpoint into a LlamaIndex Document with schema summary and readable content."""
    resp = requests.get(spec.url)
    resp.raise_for_status()
    data = resp.json()

    docs: List[Document] = []

    if spec.type == "news":
        recs  = build_news_records(data, source_url= spec.url, summarize=spec.summarize, image_base_url="https://www.hvtdpstainz.at/")
        docs  = [news_record_to_document(r, spec.url) for r in recs]

    else:
        field_lines = _build_description(data, spec.exclude_fields)

        metadata = {
            "source": spec.url,
            "endpoint_description": spec.description,
            "record_count": len(data),
            "important": spec.important,
            "Field Summary:": field_lines
            # "schema_fields": field_lines, # handy for filtering/inspection later
            # "raw_json": cleaned_json, # Keep raw JSON (pruned) in metadata for programmatic use
        }

        # Human-readable body
        records_text: List[str] = []
        for rec in _record_iter(data):
            if len(records_text) > MAX_DOC_LEN - 500:
                text = (
                        f"Source: {spec.url}\n"
                        f"Description: {spec.description}\n\n"
                        f"Data:\n" + "\n\n---\n\n".join(records_text)
                )

                docs.append(Document(text = text, metadata = metadata))
                records_text = []

            records_text.append(_format_record_to_text(rec, summarize = spec.summarize, exclude_paths=spec.exclude_fields))

        text = (
                f"Source: {spec.url}\n"
                f"Description: {spec.description}\n\n"
                #f"Field Summary:\n" + "\n".join(field_lines) + "\n\n"
                f"Data:\n" + "\n\n---\n\n".join(records_text)
        )

        docs.append(Document(text = text, metadata = metadata))

    return docs

def load_api_endpoints(specs: List[EndpointSpec]) -> List[Document]:
    """Load many endpoints and return a flat list of Documents."""
    docs: List[Document] = []
    for spec in specs:
        new_docs = load_api_data(spec)
        docs += new_docs
    return docs
