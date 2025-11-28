from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional
import requests

from llama_index.core import QueryBundle, PromptTemplate, Settings
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.base.response.schema import Response
from llama_index.core.callbacks import CallbackManager
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.memory import ChatMemoryBuffer

from engine.chat_engine import build_optimized_query_engine
from engine.smalltalk_router_wrapper import SmalltalkFirstQueryEngine
from engine.tooling_specs import HVTDP_API_GET_SPECS

DEFAULT_SYSTEM_PROMPT = (
    "Du bist ein präziser Datenassistent. Antworte NUR auf Basis der bereitgestellten JSON-Daten. "
    "Wenn die Frage nicht durch diese Daten beantwortbar ist, sage knapp, was fehlt. "
    "Formatiere kompakt (Listen/Tabellen nur wenn sinnvoll)."
)

USER_PROMPT_TEMPLATE = PromptTemplate(
    "Frage: {question}\n\n"
    "Hier sind JSON-Daten (gekürzt falls sehr groß):\n"
    "{data_json}\n\n"
    "Aufgabe:\n"
    "- Filtere/Aggregiere die Daten passend zur Frage.\n"
    "- Antworte kurz und konkret.\n"
    "- Wenn mehrere Kandidaten, gib eine kurze Liste.\n"
    "- Füge am Ende eine knappe Quellenzeile an: (Quelle: {source_url})\n"
)

CONDENSE_DE = PromptTemplate(
    """Du sollst eine eigenständige Suchfrage formulieren.

WICHTIG:
- Nutze den Chatverlauf NUR, wenn die aktuelle Nachricht eindeutig darauf verweist
  (z. B. Pronomen/Bezüge: "die", "diese", "davon", "oben genannte", "welche 5 davon", "und wer", "was davon").
- Wenn die aktuelle Nachricht für sich allein verständlich ist (keine expliziten Bezüge),
  IGNORIERE den Chatverlauf vollständig.

Gegeben:
Verlauf:
{chat_history}

Aktuelle Nachricht:
{question}

Gib NUR die umgeschriebene, eigenständige Suchfrage aus – ohne Erklärungen."""
)

class APIFetchQueryEngine(BaseQueryEngine):
    def __init__(
            self,
            url: str,
            name: str,
            description: str,
            timeout: float = 20.0,
            max_json_chars: int = 20_000,
            llm=None,
            system_prompt: str = DEFAULT_SYSTEM_PROMPT,
            callback_manager: Optional[CallbackManager] = None,
    ):
        super().__init__(callback_manager=callback_manager)
        self.url = url
        self.name = name
        self.description = description
        self.timeout = timeout
        self.max_json_chars = max_json_chars
        self.llm = llm or Settings.llm
        self.system_prompt = system_prompt

    def _fetch(self) -> Any:
        r = requests.get(self.url, timeout=self.timeout)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            # If Endpoint only returns Text (no json)
            return r.text

    def _json_snippet(self, payload: Any) -> str:
        try:
            text = json.dumps(payload, ensure_ascii=False)[: self.max_json_chars]
            return text
        except Exception:
            return str(payload)[: self.max_json_chars]

    def _ask_llm(self, question: str, data_json: str) -> str:
        prompt = USER_PROMPT_TEMPLATE.format(
            question=question,
            data_json=data_json,
            source_url=self.url
        )

        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=self.system_prompt),
            ChatMessage(role=MessageRole.USER, content=prompt),
        ]
        response = self.llm.chat(messages=messages)

        try:
            return response.message.content.strip()
        except Exception:
            try:
                return response.text.strip()
            except Exception:
                return str(response).strip()

    def _query(self, query_bundle: QueryBundle) -> Response:
        query = query_bundle.query_str if isinstance(query_bundle, QueryBundle) else str(query_bundle)
        payload = self._fetch()
        data_json = self._json_snippet(payload)
        answer = self._ask_llm(query, data_json)

        # Optional
        header = f"[{self.name}] {self.description}\n"
        return Response(header + "\n" + answer.strip())

    async def _aquery(self, query_bundle: QueryBundle) -> Response:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._query, query_bundle)

    def _get_prompt_modules(self) -> Dict[str, Any]:
        return {}

def build_tools(extra_tools: Optional[List[QueryEngineTool]] = None,) -> List[QueryEngineTool]:
    tools: List[QueryEngineTool] = []

    if extra_tools:
        for tool in extra_tools:
            tools.append(tool)

    for spec in HVTDP_API_GET_SPECS:
        query_engine = APIFetchQueryEngine(url=spec.url, name=spec.name, description=spec.description)

        tools.append(
            QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name=spec.name,
                    description=f"{spec.description} (Quelle: {spec.url})",
                ),
            )
        )

    return tools

def build_router_chat_with_tools(
        extra_tools: Optional[List[QueryEngineTool]] = None,
        memory_k: int = 2000,
):
    tools = build_tools(extra_tools=extra_tools)

    router = RouterQueryEngine.from_defaults(query_engine_tools=tools)
    safe_router = SmalltalkFirstQueryEngine(router_qe=router, llm=Settings.llm)

    chat = CondenseQuestionChatEngine.from_defaults(
        query_engine=safe_router,
        memory=ChatMemoryBuffer.from_defaults(token_limit=memory_k),
        condense_question_prompt=CONDENSE_DE
    )
    return chat, tools

def wrap_rag_as_tool(index) -> QueryEngineTool:
    #qe = index.as_query_engine(similarity_top_k=12)
    qe = build_optimized_query_engine(index)
    return QueryEngineTool(
        query_engine=qe,
        metadata=ToolMetadata(
            name="club_rag",
            description="Liefert alle Vereinsdaten (News, Versammlungen, Events, Entenlauf, Entenlose, Kontakt, Trainingsbeteiligung).",
        ),
    )
