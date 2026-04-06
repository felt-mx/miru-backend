import socketio
from fastapi import FastAPI
from app.api.socket.events import sio

app = FastAPI()
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


@app.get("/health")
def health():
    return {"status": "ok"}


app = socket_app
