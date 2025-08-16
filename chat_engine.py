from llama_index.core import VectorStoreIndex
from llama_index.core.chat_engine.types import ChatMode
from llama_index.core.memory import ChatMemoryBuffer

def build_chat_engine(index: VectorStoreIndex, token_limit: int = 4000):
    # In-memory conversation buffer (not persisted)
    memory = ChatMemoryBuffer.from_defaults(token_limit=token_limit)

    # Chat engine that condenses follow-ups and pulls context from your index
    chat_engine = index.as_chat_engine(
        chat_mode = ChatMode.CONDENSE_PLUS_CONTEXT, #condenses conversation, then uses context to answer
        memory=memory,
    )

    return chat_engine
