from llama_index.core import Document, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI

from config import OPENAI_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP

def summarize_doc(
        doc: Document,
        #llm=Ollama(model="llama3.1:8b-instruct", temperature=0),
        llm=OpenAI(model = "gpt-3.5-turbo", temperature = 0.0, api_key = OPENAI_API_KEY),
        language="Deutsch",
        max_words=250,
        mode: ResponseMode = ResponseMode.TREE_SUMMARIZE,
) -> str:
    # chunking so that the summarizer can see the whole text reliably
    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separator="\n\n")
    nodes = splitter.get_nodes_from_documents([doc])

    # Build a small summarization index over the chunks
    sidx = SummaryIndex(nodes)

    # Use a strong multi-chunk summarization mode
    qe = sidx.as_query_engine(response_mode=mode, llm=llm)

    prompt = (
        f"Erstelle eine prägnante, sachliche Zusammenfassung des Dokuments auf {language}. "
        f"Maximal {max_words} Wörter. Behalte Personen, Daten, Zahlen und Kernaussagen bei. "
        "Keine Spekulationen, keine externen Fakten."
    )
    resp = qe.query(prompt)
    return str(resp).strip()


def summarize_text(
        text: str,
        *,
        #llm = Ollama(model="llama3.1:8b-instruct", temperature=0),
        llm=OpenAI(model = "gpt-3.5-turbo", temperature = 0.0, api_key = OPENAI_API_KEY),
        language="Deutsch",
        max_words: int = 250,
        mode: ResponseMode = ResponseMode.TREE_SUMMARIZE,
) -> str:
    """Chunk long news text and summarize with a LLM."""

    return summarize_doc(
        doc=Document(text=text),
        llm=llm,
        language=language,
        max_words=max_words,
        mode=mode,
    )
