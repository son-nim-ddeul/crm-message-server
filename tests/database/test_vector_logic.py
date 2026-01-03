import pytest
from unittest.mock import MagicMock, patch
from database.vector_manager import VectorManager
from database.embeddings import EmbeddingManager
from sqlalchemy import create_engine, event
from src.database.session import load_vec_extension

@pytest.fixture
def mock_vector_manager():
    # 테스트용 메모리 DB 엔진 생성
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    event.listen(engine, "connect", load_vec_extension)
    
    # EmbeddingManager 모킹
    mock_emb = MagicMock(spec=EmbeddingManager)
    
    # VectorManager의 engine을 메모리 DB로 교체
    with patch("database.vector_manager.vector_engine", engine):
        vm = VectorManager(embedding_manager=mock_emb)
        yield vm, mock_emb


def test_vector_manager_insert_and_search(mock_vector_manager):
    vm, mock_emb = mock_vector_manager
    
    # 1. 데이터 삽입 테스트 데이터 준비
    test_data = [
        {"key": "model_a", "content": "삼성 갤럭시 스마트폰", "vec": [0.1] * 768},
        {"key": "model_b", "content": "애플 아이폰 시리즈", "vec": [0.5] * 768},
        {"key": "model_c", "content": "구글 픽셀 폰", "vec": [0.9] * 768},
    ]
    
    # embed_text가 호출될 때마다 준비된 벡터 반환하도록 설정
    mock_emb.embed_text.side_effect = [d["vec"] for d in test_data]
    
    # 데이터 삽입
    for d in test_data:
        vm.add_item(key=d["key"], content=d["content"], metadata={"model_info": d["key"]})
    
    # 2. 유사도 조회 테스트
    # "갤럭시"와 비슷한 데이터를 찾기 위해 query_vec를 [0.12]로 설정 (mock_emb.embed_text가 호출됨)
    mock_emb.embed_text.side_effect = None
    mock_emb.embed_text.return_value = [0.12] * 768
    
    results = vm.search_similar("갤럭시와 비슷한 것은?", limit=2)
    
    # 검증: 가장 가까운 순서대로 리스트 조회되는지 확인
    assert len(results) == 2
    assert results[0]["key"] == "model_a"  # [0.1]이 [0.12]와 가장 가까움
    assert results[1]["key"] == "model_b"  # [0.5]가 그다음 가까움
    assert "model_info" in results[0]["metadata"]
    assert results[0]["metadata"]["model_info"] == "model_a"

def test_vector_manager_list_results(mock_vector_manager):
    vm, mock_emb = mock_vector_manager
    
    # 데이터 삽입
    mock_emb.embed_text.return_value = [0.1] * 768
    vm.add_item(key="test_key", content="테스트 콘텐츠")
    
    # 조회
    mock_emb.embed_text.return_value = [0.1] * 768
    results = vm.search_similar("테스트", limit=10)
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert "key" in results[0]
    assert "content" in results[0]
    assert "distance" in results[0]

