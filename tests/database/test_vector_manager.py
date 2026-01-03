import pytest
import json
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine, event
from src.database.session import load_vec_extension
from database.vector_manager import VectorManager
from database.embeddings import EmbeddingManager
from src.message.schemas import MessageReferenceBase

# 실제 API 호출 여부 설정 (True로 변경 시 실제 Gemini API 호출)
USE_REAL_API = False


@pytest.fixture
def vector_manager_fixture():
    # 테스트용 메모리 DB 엔진 생성
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    event.listen(engine, "connect", load_vec_extension)
    
    if USE_REAL_API:
        # 실제 EmbeddingManager 사용, 하지만 DB는 메모리 DB 사용
        vm = VectorManager(engine=engine)
        yield vm, vm.embedding_manager
    else:
        # EmbeddingManager 모킹 (API 호출 방지)
        mock_emb = MagicMock(spec=EmbeddingManager)
        vm = VectorManager(embedding_manager=mock_emb, engine=engine)
        yield vm, mock_emb


def test_vector_search_by_title_and_content(vector_manager_fixture):
    """
    MessageReferenceBase 스키마를 사용하여 데이터를 삽입하고,
    title과 content를 기반으로 유사도 검색이 정상적으로 동작하는지 테스트합니다.
    """
    vm, mock_emb = vector_manager_fixture
    
    # 1. MessageReferenceBase 모킹 데이터 준비
    mock_data = [
        MessageReferenceBase(
            title="여름 시즌 세일 안내",
            content="전 품목 30% 할인 혜택을 드립니다. 여름 휴가 준비하세요!",
            category="PROMOTION"
        ),
        MessageReferenceBase(
            title="신규 회원 가입 감사 쿠폰",
            content="가입을 축하드립니다. 웰컴 쿠폰 5,000원이 발급되었습니다.",
            category="COUPON"
        ),
        MessageReferenceBase(
            title="포인트 소멸 예정 알림",
            content="보유하신 포인트 1,000점이 이번 달 말에 소멸될 예정입니다.",
            category="NOTICE"
        )
    ]
    
    # 2. 고정된 벡터 값 설정 (검색 결과 확인용)
    # 첫 번째: [0.1...], 두 번째: [0.5...], 세 번째: [0.9...]
    vectors = [
        [0.1] * 768,
        [0.5] * 768,
        [0.9] * 768
    ]
    
    # mock_emb.embed_text가 호출될 때마다 준비된 벡터를 순서대로 반환
    # 마지막에 검색 쿼리용 벡터([0.48] * 768)를 추가하여 두 번째 데이터와 가장 가깝게 만듦
    query_vector = [0.48] * 768
    
    if not USE_REAL_API:
        mock_emb.embed_text.side_effect = vectors + [query_vector]
    
    # 3. 데이터 삽입 (title과 content를 조합하여 저장)
    for ref in mock_data:
        combined_text = f"제목: {ref.title}\n내용: {ref.content}"
        vm.add_item(
            key=ref.title,
            content=combined_text,
            metadata={"category": ref.category}
        )
    
    # 4. 유사도 기반 조회 실행
    # "쿠폰"이나 "가입" 키워드가 포함된 쿼리를 가정
    search_query = "회원 가입하면 어떤 혜택이 있나요?"
    print(f"\n[테스트 정보] 실제 API 사용 여부: {USE_REAL_API}")
    print(f"[검색 쿼리] {search_query}")
    
    results = vm.search_similar(search_query, limit=2)
    
    # 5. 검증
    assert len(results) == 2
    
    # 결과 로그 출력
    for i, res in enumerate(results):
        print(f"[결과 {i+1}] 키: {res['key']}, 유사도(거리): {res['distance']:.4f}")
        print(f"         내용 요약: {res['content'][:30]}...")
    
    if not USE_REAL_API:
        # 모킹 모드일 때만 특정 순서와 벡터 값 기반 검증 수행
        # [0.48]과 [0.5]의 거리가 가장 가까움
        assert results[0]["key"] == "신규 회원 가입 감사 쿠폰"
        assert results[0]["metadata"]["category"] == "COUPON"
        assert "웰컴 쿠폰" in results[0]["content"]
        
        # 두 번째로 가까운 데이터(첫 번째 데이터) 확인
        # [0.48]과 [0.1]의 거리가 [0.48]과 [0.9]의 거리보다 가까움
        assert results[1]["key"] == "여름 시즌 세일 안내"
        
        # 조회된 결과 리스트의 정렬 상태 확인 (distance 오름차순)
        assert results[0]["distance"] < results[1]["distance"]
    else:
        # 실제 API 호출 시에는 결과가 존재하고 distance가 정렬되어 있는지만 확인
        assert results[0]["distance"] <= results[1]["distance"]


def test_vector_search_no_results(vector_manager_fixture):
    """데이터가 없을 때 빈 리스트를 반환하는지 테스트"""
    vm, mock_emb = vector_manager_fixture
    
    if not USE_REAL_API:
        mock_emb.embed_text.return_value = [0.0] * 768
    
    results = vm.search_similar("아무거나", limit=5)
    assert isinstance(results, list)
    assert len(results) == 0
