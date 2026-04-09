from app.agents.vision_agent.system_prompt import get_system_prompt


def _format_image_url(img_data: str, media_type: str = "image/jpeg") -> str:
    if img_data.startswith("data:"):
        return img_data
    return f"data:{media_type};base64,{img_data}"


def build_prompt(frame_b64: str, context: str):
    prompt = []

    system_prompt = get_system_prompt(context=context)

    prompt.append({"role": "system", "content": system_prompt})

    prompt.append({
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe the image in one to two sentences at most."},
            {"type": "image_url", "image_url": {
                "url": _format_image_url(frame_b64)}}
        ]
    })

    return prompt
