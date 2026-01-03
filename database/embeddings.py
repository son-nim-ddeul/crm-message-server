import os
from google import genai
from src.config import settings

class EmbeddingManager:
    def __init__(self, model_name: str = None):
        api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name or settings.embedding_model

    def embed_text(self, text: str) -> list[float]:
        """텍스트를 벡터로 변환합니다."""
        if not text:
            return []
            
        result = self.client.models.embed_content(
            model=self.model_name,
            contents=text
        )
        return result.embeddings[0].values

