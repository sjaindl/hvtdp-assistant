from typing import List, Dict, Any, Iterable

from llama_index.core import Document
from datetime import datetime

from utils.html_utils import html_to_text, norm_date, abs_url
from utils.summarizer import summarize_text

def build_news_records(
        api_payload: Any,
        *,
        source_url: str,
        summarize: bool,
        image_base_url: str = "https://www.hvtdpstainz.at/"
) -> List[Dict[str, Any]]:
    """
    Convert the raw API JSON into a normalized list of 'rec' dicts
    """
    # The API returns a top-level list of items
    items: Iterable[dict] = api_payload if isinstance(api_payload, list) else api_payload.get("data", [])
    out: List[Dict[str, Any]] = []

    for it in items:
        # Raw fields (string or blank)
        news_id   = (it.get("newsId") or "").strip()
        news_date = norm_date(it.get("newsDate") or "")
        title     = (it.get("title") or "").strip()
        html_news = it.get("htmlNews") or ""
        news_text = it.get("news") or ""

        # Convenience fields
        img_home  = abs_url(image_base_url, it.get("imagePathHome"))
        img_full  = abs_url(image_base_url, it.get("imagePath"))

        # Compute a clean plain-text body (prefer htmlNews if present)
        body_plain = html_to_text(html_news) if html_news else " ".join(news_text.split())
        summary = summarize_text(body_plain) if summarize else body_plain

        rec = {
            # minimal canonical fields
            "newsId": news_id,
            "newsDate": news_date,
            "title": title,
            "htmlNews": html_news,
            "news": news_text,
            "body_plain": body_plain,
            "summary": summary,

            # convenience / optional
            "imageUrlHome": img_home,
            "imageUrl": img_full,
            "source": source_url,
            "type": "news",
        }
        out.append(rec)

    return out

def news_record_to_document(rec: dict, source_url: str) -> Document:
    title = rec.get("title") or ""
    date_raw = rec.get("newsDate") or ""
    # normalize date
    try:
        date_iso = datetime.fromisoformat(date_raw).date().isoformat()
    except Exception:
        date_iso = date_raw

    summary = rec.get("summary") or ""
    text = f"{title}\n{date_iso}\n\n{summary}"

    meta = {
        "source": source_url,
        "type": "news",
        "newsId": rec.get("newsId"),
        "newsDate": date_iso,
        "title": title,
        "important": False,
    }
    return Document(text = text, metadata = meta)
