from typing import AsyncIterator, Literal, TypedDict
from app.agents.query_agent.prompt_builder import build_prompt
from app.core.generator import Generator


class StreamChunk(TypedDict):
    type: Literal["reasoning", "content"]
    content: str


class QueryAgent:
    def __init__(self):
        self.generator = Generator()

    async def query_agent(
        self,
        query: str,
        files: list,
        thinking: bool,
        settings: dict,
        chat_messages: list[dict] | None = None,
        context: str | None = None,
        frame_b64: str | None = None,
    ) -> AsyncIterator[StreamChunk]:
        messages = build_prompt(query, files or [], chat_messages or [], context=context, frame_b64=frame_b64)

        async for chunk_type, token in self.generator.stream(messages, enable_thinking=thinking, settings=settings):
            yield {"type": chunk_type, "content": token}
