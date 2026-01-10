import json
from database.vector_manager import VectorManager


def find_previous_messages(message_info: dict, top_k: int) -> list[dict]:
    vector_manager = VectorManager()
    results = vector_manager.search_similar(content=json.dumps(message_info, ensure_ascii=False), limit=top_k)
    return results
