import socketio
from app.agents.query_agent.query_agent import QueryAgent
from app.sessions import session_store

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=10,
    ping_timeout=30,
    max_http_buffer_size=5242880,
)


@sio.event
async def connect(sid, environ):
    session_store.get_or_create(sid)
    print(f"[WebSocket] Client connected: {sid}")


@sio.event
async def disconnect(sid):
    session_store.destroy(sid)
    print(f"[WebSocket] Client disconnected: {sid}")


@sio.event
async def user_message(sid, data):
    session = session_store.get_or_create(sid)
    query = data.get("text", "")
    thinking = data.get("thinking", False)
    settings = data.get("settings", {})
    files = data.get("files", [])

    if not query:
        await sio.emit("error", "Text is required", to=sid)
        return

    query_agent = QueryAgent()
    final_output = []

    try:
        async for chunk in query_agent.query_agent(
            query,
            files,
            thinking,
            settings,
            chat_messages=session.chat_messages,
        ):
            if chunk["type"] in ["reasoning"]:
                await sio.emit("assistant_thinking", chunk["content"], to=sid)
            elif chunk["type"] == "content":
                final_output.append(chunk["content"])
                await sio.emit("assistant_token", chunk["content"], to=sid)

    except Exception as e:
        await sio.emit("error", str(e), to=sid)
        return

    final_output = "".join(final_output)

    await sio.emit("assistant_done", to=sid)

    session.chat_messages.append({"role": "user", "content": query})
    session.chat_messages.append(
        {"role": "assistant", "content": final_output})

    entry = session_store.make_entry("query", description=final_output)
    session.append(entry)

    await sio.emit("session_log", session_store.entry_event(entry), to=sid)
