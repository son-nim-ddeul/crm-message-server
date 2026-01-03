import json
from sqlalchemy import text
from tests.database.test_models import MockItem


def test_rds_operations(rds_session):
    """RDS (SQLite)의 기본적인 CRUD 기능을 테스트합니다."""
    db = rds_session
    # 1. Create
    test_name = "테스트 아이템"
    test_description = "테스트 아이템 설명입니다."
    item = MockItem(name=test_name, description=test_description)
    db.add(item)
    db.commit()
    db.refresh(item)
    assert item.id is not None

    # 2. Read
    item_read = (
        db.query(MockItem)
        .filter(MockItem.name == test_name)
        .first()
    )
    assert item_read is not None
    assert item_read.description == test_description

    # 3. Update
    updated_description = "수정된 설명입니다."
    item_read.description = updated_description
    db.commit()
    db.refresh(item_read)
    assert item_read.description == updated_description

    # 4. Delete
    db.delete(item_read)
    db.commit()
    item_deleted = db.query(MockItem).filter(MockItem.name == test_name).first()
    assert item_deleted is None


def test_vector_operations(vector_session):
    """sqlite-vec을 이용한 벡터 DB의 가상 테이블 생성, 삽입, 검색을 테스트합니다."""
    db = vector_session
    # 1. 벡터 가상 테이블 생성 (4차원 벡터 예시)
    db.execute(text("DROP TABLE IF EXISTS vec_items"))
    db.execute(text("CREATE VIRTUAL TABLE vec_items USING vec0(embedding float[4])"))
    db.commit()

    # 2. 벡터 데이터 삽입
    # vec_f32 함수를 통해 JSON 문자열 리스트를 바이너리로 변환하여 삽입합니다.
    vec1 = json.dumps([0.1, 0.2, 0.3, 0.4])
    vec2 = json.dumps([0.5, 0.6, 0.7, 0.8])

    db.execute(
        text("INSERT INTO vec_items(rowid, embedding) VALUES (:id, vec_f32(:vec))"),
        {"id": 1, "vec": vec1}
    )
    db.execute(
        text("INSERT INTO vec_items(rowid, embedding) VALUES (:id, vec_f32(:vec))"),
        {"id": 2, "vec": vec2}
    )
    db.commit()

    # 3. 벡터 유사도 검색 (K-Nearest Neighbors)
    # 쿼리 벡터와 가장 가까운 1개의 항목을 찾습니다.
    query_vec = json.dumps([0.1, 0.2, 0.3, 0.35])
    results = db.execute(
        text("""
            SELECT 
                rowid, 
                distance 
            FROM vec_items 
            WHERE embedding MATCH vec_f32(:query_vec)
            AND k = 1
        """),
        {"query_vec": query_vec}
    ).fetchall()

    assert len(results) == 1
    assert results[0][0] == 1  # vec1과 더 가까우므로 rowid 1이 반환되어야 함

    # 4. 데이터 삭제
    db.execute(text("DELETE FROM vec_items WHERE rowid = 1"))
    db.commit()

    res_after_delete = (
        db
        .execute(text("SELECT rowid FROM vec_items WHERE rowid = 1"))
        .fetchone()
    )
    assert res_after_delete is None

