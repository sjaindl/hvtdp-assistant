# smalltalk_router_wrapper.py
from typing import Optional, Dict, Any
import re, asyncio
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.response.schema import Response
from llama_index.core.callbacks import CallbackManager
from llama_index.core.schema import QueryBundle
from llama_index.core import Settings

SMALLTALK_RE = re.compile(
    r"^\s*(hi|hallo|hello|servus|moin|grüß|gruess|hey|yo|guten (morgen|tag|abend)|"
    r"danke|thanks|thx|wie geht|wie läufts|na\?)\b",
    re.IGNORECASE,
)

def _is_smalltalk(q: str) -> bool:
    # greeting/thanks or very short text:
    return bool(SMALLTALK_RE.search(q)) or len(q.strip()) <= 3

class SmalltalkFirstQueryEngine(BaseQueryEngine):
    def __init__(self, router_qe: BaseQueryEngine, llm=None, callback_manager: Optional[CallbackManager] = None):
        super().__init__(callback_manager=callback_manager)
        self.router_qe = router_qe
        self.llm = llm or Settings.llm

    def _query(self, query_bundle: QueryBundle) -> Response:
        q = query_bundle.query_str if isinstance(query_bundle, QueryBundle) else str(query_bundle)
        if _is_smalltalk(q):
            msg = (
                "Hallo Sportsfreund! Ich bin der HV TDP Assistant und beantworte dir gerne alle Fragen rund um den HV TDP Stainz!"
                "Du kannst z. B. fragen: „Wer ist der Tormann?“, „Zeig mir die Tabelle von 2024“, "
                "oder „Welche Vereinsveranstaltungen gab es 2023?“"
            )
            return Response(msg)
        return self.router_qe.query(query_bundle)

    async def _aquery(self, query_bundle: QueryBundle) -> Response:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._query, query_bundle)

    def _get_prompt_modules(self) -> Dict[str, Any]:
        return {}
