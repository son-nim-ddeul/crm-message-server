import json
from sqlalchemy import text
from src.database.session import vector_engine
from .embeddings import EmbeddingManager


class VectorManager:
    def __init__(self, embedding_manager: EmbeddingManager = None, engine=None):
        self.engine = engine or vector_engine
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self._init_db()

    def _init_db(self):
        """벡터 테이블 및 메타데이터 테이블 초기화"""
        with self.engine.begin() as conn:
            # 메타데이터 테이블 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS item_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT,
                    content TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 벡터 가상 테이블 생성 (768차원)
            # sqlite-vec v0.1.x syntax: vec0
            # Note: rowid in virtual table will match id in item_metadata
            conn.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_items USING vec0(
                    embedding float[768]
                )
            """))

    def add_item(self, key: str, content: str, metadata: dict = None):
        """데이터 임베딩 후 벡터 DB에 저장"""
        embedding = self.embedding_manager.embed_text(content)
        metadata_json = json.dumps(metadata or {})
        
        with self.engine.begin() as conn:
            # 1. 메타데이터 저장
            result = conn.execute(
                text("INSERT INTO item_metadata (key, content, metadata) VALUES (:key, :content, :metadata)"),
                {"key": key, "content": content, "metadata": metadata_json}
            )
            item_id = result.lastrowid
            
            # 2. 벡터 저장 (vec_f32 사용)
            conn.execute(
                text("INSERT INTO vec_items(rowid, embedding) VALUES (:id, vec_f32(:vec))"),
                {"id": item_id, "vec": json.dumps(embedding)}
            )
        return item_id

    def search_similar(self, query: str, limit: int = 5):
        """유사도 기반 검색"""
        query_embedding = self.embedding_manager.embed_text(query)
        
        with self.engine.connect() as conn:
            results = conn.execute(
                text("""
                    SELECT 
                        m.key,
                        m.content,
                        m.metadata,
                        v.distance
                    FROM vec_items v
                    JOIN item_metadata m ON v.rowid = m.id
                    WHERE v.embedding MATCH vec_f32(:query_vec)
                    AND k = :limit
                    ORDER BY v.distance ASC
                """),
                {
                    "query_vec": json.dumps(query_embedding),
                    "limit": limit
                }
            ).fetchall()
            
        return [
            {
                "key": r[0],
                "content": r[1],
                "metadata": json.loads(r[2]),
                "distance": r[3]
            }
            for r in results
        ]

