import os
from dataclasses import dataclass
from pathlib import Path

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
        critic_model (str): Model for evaluation tasks.
        worker_model (str): Model for working/generation tasks.
        max_search_iterations (int): Maximum search iterations allowed.
    """

    write_model: str = "gemini-3-pro-preview"
    critic_model: str = "gemini-3-pro-preview"
    worker_model: str = "gemini-3-pro-preview"
    max_search_iterations: int = 3


config = ResearchConfiguration()