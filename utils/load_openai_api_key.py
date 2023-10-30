import os
from pathlib import Path

import environ


def load_openai_api_key():
    env = environ.Env()
    environ.Env.read_env(str(Path().parent / ".env"))
    os.environ["OPENAI_API_KEY"] = env("OPENAI_API_KEY")
