# TODO: before_agent_callback 활용하여
# 모든 message_type의 message output에 대해
# 1. message_sending_datetime state에서 잡아서 구체화 및 없다면 미정이라고 적어야함
# 구체화 : 계절, 요일, 공휴일 여부, 근접 공휴일 리스트 를 의미한다.
# 2. temp:{message_type.value}_previous_message 설정
#  이때 previous_message 는
#  a. RAG로 content 및 metadata를 조회한다.
#    => 없다면 과거 메시지 발송 이력 중, 확인되는 유사 메시지 내용이 없다고 넣는다.
#  b. metadata의 message_sending_datetime를 바탕으로 1.구체화 및 결과를 포맷팅한다.


import json
from database.vector_manager import VectorManager


def find_previous_messages(message_info: dict, top_k: int) -> list[dict]:
    vector_manager = VectorManager()
    results = vector_manager.search_similar(content=json.dumps(message_info, ensure_ascii=False), limit=top_k)
    return results
