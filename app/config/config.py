from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    def __init__(self):
        self.OPENAI_API_URL = os.getenv("OPENAI_API_URL")
        self.OPENAI_GEN_API_PORT = os.getenv("OPENAI_GEN_API_PORT")
        self.OPENAI_GEN_MODEL_NAME = os.getenv("OPENAI_GEN_MODEL_NAME")
        self.session_log_limit = 200
        self.context_recent_k = 5

    @property
    def OPENAI_GEN_API_URL(self):
        return f"http://{self.OPENAI_API_URL}:{self.OPENAI_GEN_API_PORT}"


config = Config()
