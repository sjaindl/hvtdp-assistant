from urllib.parse import urljoin
from datetime import datetime
from html import unescape
from bs4 import BeautifulSoup

def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for t in soup(["script", "style", "noscript", "svg", "iframe"]):
        t.decompose()

    text = soup.get_text(separator = " ", strip = True)
    # unescape HTML entities and normalize whitespace
    return " ".join(unescape(text).split())

def norm_date(s: str) -> str:
    if not s:
        return ""
    try:
        # API returns ISO like "2025-07-09"
        return datetime.fromisoformat(s).date().isoformat()
    except Exception:
        return s  # leave as-is if unknown format

def abs_url(base: str, path: str) -> str:
    # path in API looks like "news/xxx.jpg"
    return urljoin(base, path)
