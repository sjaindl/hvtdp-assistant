from llama_index.core.schema import Document
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import PDFReader
import os
import pandas as pd

from utils.summarizer import summarize_doc

def load_local_docs(folder = "docs"):
    docs = []
    docs += load_pdfs(folder)
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            docs += load_csv(os.path.join(folder, file))
    return docs

def load_csv(path):
    df = pd.read_csv(path)
    text = df.to_string(index = False)
    return [Document(text = text, metadata = {"source": path})]

def load_pdfs(path):
    parser = PDFReader()
    file_extractor = {".pdf": parser}
    reader = SimpleDirectoryReader(
        path, file_extractor = file_extractor
    )

    data = reader.load_data()

    out = []
    for d in data:
        summary = summarize_doc(d)
        meta = d.metadata
        out.append(Document(text=summary, metadata=meta))

    return out
