from app.agents.query_agent.system_prompt import get_system_prompt


def _format_image_url(img_data: str, media_type: str = "image/jpeg") -> str:
    if img_data.startswith("data:"):
        return img_data
    return f"data:{media_type};base64,{img_data}"


def _extract_image_payload(image_item):
    if isinstance(image_item, str):
        return image_item, "image/jpeg"

    if not isinstance(image_item, dict):
        return "", "image/jpeg"

    img_data = image_item.get("data") or image_item.get("url") or ""
    media_type = image_item.get("type") or "image/jpeg"

    if not isinstance(img_data, str):
        return "", "image/jpeg"

    if not isinstance(media_type, str) or not media_type.startswith("image/"):
        media_type = "image/jpeg"

    return img_data, media_type


def build_prompt(query, images=None, chat_messages=None):
    prompt = []

    system_content = get_system_prompt()

    prompt.append({"role": "system", "content": system_content})

    if chat_messages:
        for message in chat_messages[-6:]:  # Keep context window manageable
            prompt.append(message.copy())

    user_content = []

    if query:
        user_content.append({"type": "text", "text": query})

    if images:
        for img in images:
            img_str, media_type = _extract_image_payload(img)
            if img_str:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": _format_image_url(img_str, media_type)
                    }
                })

    new_message = {"role": "user", "content": user_content}

    prompt.append(new_message)

    return prompt
