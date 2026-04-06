import httpx
import json
from app.config.config import Config


class Generator:
    def __init__(self, config: Config = Config()):
        self.config = config

    async def stream(self, messages, enable_thinking=False, settings=None):
        payload = {
            "model": self.config.OPENAI_GEN_MODEL_NAME,
            "messages": messages,
            "stream": True,
            "chat_template_kwargs": {
                "enable_thinking": enable_thinking,
            }
        }

        if settings:
            payload["temperature"] = settings.get("temperature", 0.7)
            payload["top_p"] = settings.get("top_p", 0.8)
            payload["top_k"] = settings.get("top_k", 20)
            payload["min_p"] = settings.get("min_p", 0.0)
            payload["presence_penalty"] = settings.get("presence_penalty", 1.5)
            payload["repetition_penalty"] = settings.get(
                "repetition_penalty", 1.0)

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.config.OPENAI_GEN_API_URL}/v1/chat/completions",
                json=payload,
            ) as response:
                if response.status_code != 200:
                    error_body = await response.aread()
                    raise Exception(
                        f"OpenAI Generation Error {response.status_code}: {error_body.decode()}"
                    )

                async for line in response.aiter_lines():
                    if not line or not line.strip():
                        continue

                    if line.startswith("data: "):
                        line = line[6:]

                    if line.strip() == "[DONE]":
                        break

                    try:
                        data = json.loads(line)

                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})

                            reasoning = delta.get("reasoning") or delta.get(
                                "reasoning_content")

                            if reasoning:
                                yield ("reasoning", reasoning)

                            content = delta.get("content", "")

                            if content:
                                yield ("content", content)
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        continue

    async def generate(self, messages, enable_thinking=False, settings=None):
        payload = {
            "model": self.config.OPENAI_GEN_MODEL_NAME,
            "messages": messages,
            "stream": False,
            "chat_template_kwargs": {
                "enable_thinking": enable_thinking,
            }
        }

        if settings:
            payload["temperature"] = settings.get("temperature", 0.7)
            payload["top_p"] = settings.get("top_p", 0.8)
            payload["top_k"] = settings.get("top_k", 20)
            payload["min_p"] = settings.get("min_p", 0.0)
            payload["presence_penalty"] = settings.get("presence_penalty", 1.5)
            payload["repetition_penalty"] = settings.get(
                "repetition_penalty", 1.0)

        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                f"{self.config.OPENAI_GEN_API_URL}/v1/chat/completions",
                json=payload,
            )

            if response.status_code != 200:
                error_body = await response.aread()
                raise Exception(
                    f"OpenAI Generation Error {response.status_code}: {error_body.decode()}"
                )

            response_data = response.json()

            if isinstance(response_data, dict):
                if "message" in response_data:
                    return response_data["message"]
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    choice = response_data["choices"][0]
                    if (
                        isinstance(choice, dict)
                        and "message" in choice
                        and isinstance(choice["message"], dict)
                    ):
                        return choice["message"]
                    if "text" in choice:
                        return choice.get("text", "")
