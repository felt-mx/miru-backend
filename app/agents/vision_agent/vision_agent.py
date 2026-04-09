from app.agents.vision_agent.prompt_builder import build_prompt
from app.core.generator import Generator


class VisionAgent:
    def __init__(self):
        self.generator = Generator()

    async def run(self, frame_b64: str, context: str) -> str | None:
        prompt = build_prompt(frame_b64=frame_b64, context=context)
        return await self.generator.generate(prompt)
