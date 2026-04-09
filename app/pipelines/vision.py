import asyncio
from app.sessions import session_store
from app.sessions.session_store import make_entry
from app.utils.diff import b64_to_array, pixel_diff
from app.config.config import config
from app.agents.vision_agent.vision_agent import VisionAgent

vision_agent = VisionAgent()
_locks: dict[str, asyncio.Lock] = {}


def _get_lock(sid: str) -> asyncio.Lock:
    if sid not in _locks:
        _locks[sid] = asyncio.Lock()
    return _locks[sid]


async def process_frame(sid: str, frame_b64: str) -> None:
    lock = _get_lock(sid)

    if lock.locked():
        return

    async with lock:
        session = session_store.get_or_create(sid)

        try:
            curr_arr = b64_to_array(frame_b64)
        except Exception as e:
            return

        prev_arr = session.get_last_frame_arr()
        if prev_arr is not None:
            diff = pixel_diff(prev_arr, curr_arr)
            if diff < config.diff_threshold:
                session.set_last_frame(frame_b64, curr_arr)
                return

        session.set_last_frame(frame_b64, curr_arr)

        context = session.build_context()
        try:
            output = await vision_agent.run(frame_b64=frame_b64, context=context)
        except Exception as e:
            return

        entry = make_entry(
            "vision", description=output["content"], frame_b64=frame_b64)
        session.append(entry)

        return entry
