import os
from dataclasses import dataclass
from pathlib import Path
from google.adk.models.google_llm import Gemini
from google.genai import types

from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

if os.getenv("GOOGLE_API_KEY"):
    # AI Studio mode (default): Use API key authentication
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")
else:
    raise Exception("Google Api Key가 확인되지 않습니다.")

@dataclass
class ResearchConfiguration:
    """Configuration for research-related models and parameters.

    Attributes:
        writer_model (str): Model for writing tasks.
        critic_model (str): Model for evaluation tasks.
        worker_model (str): Model for working/generation tasks.
        max_search_iterations (int): Maximum search iterations allowed.
    """

    # gemini-3-pro-preview
    # writer_model: str = "gemini-2.5-flash"
    # critic_model: str = "gemini-2.5-flash"
    # worker_model: str = "gemini-2.5-flash"
    writer_model = Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(initial_delay=10, attempts=10)
    )
    critic_model = Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(initial_delay=10, attempts=10)
    )
    worker_model= Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(initial_delay=10, attempts=10)
    )
    max_search_iterations: int = 3


config = ResearchConfiguration()