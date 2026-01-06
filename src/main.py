from contextlib import asynccontextmanager
from typing import List, Union
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.config import settings
from src.message.router import router as message_router
from src.runner.runner import initialize_adk_services
from database.vector_manager import VectorManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # (필요시) 시작 시 실행할 코드
    initialize_adk_services()
    yield
    # (필요시) 종료 시 실행할 코드


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=settings.docs_url,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


app.include_router(message_router, prefix="/messages", tags=["Message"])


@app.post("/vectors/upload", tags=["Vector"])
async def upload_vectors(data: Union[dict, List[dict]] = Body(...)):
    """
    벡터 데이터를 대량으로 업로드합니다.
    dummy_list.json과 같은 형식을 지원합니다.
    """
    if isinstance(data, dict):
        items = [data]
    elif isinstance(data, list):
        items = data
    else:
        raise HTTPException(status_code=400, detail="Invalid data format. Expected dict or list of dicts.")

    from pprint import pprint
    pprint(items)

    vm = VectorManager()
    success_count = 0
    duplicate_count = 0
    
    for idx, item in enumerate(items):
        content = item.get("content")
        metadata = item.get("metadata")
        
        # 유효성 검사: content(str), metadata(dict)
        if not isinstance(content, str):
            logger_msg = f"Item at index {idx} skipped: content is not a string"
            print(logger_msg)
            continue
        if not isinstance(metadata, dict):
            logger_msg = f"Item at index {idx} skipped: metadata is not a dictionary"
            print(logger_msg)
            continue

        # 중복 체크 (동일한 content가 이미 존재하는지 확인)
        with vm.engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM item_metadata WHERE content = :content LIMIT 1"),
                {"content": content}
            ).fetchone()
            
            if exists:
                duplicate_count += 1
                continue
            
        # key는 metadata에서 가져오거나 기본값 사용
        key = metadata.get("key", "manual_upload")
        
        try:
            vm.add_item(key=key, content=content, metadata=metadata)
            success_count += 1
        except Exception as e:
            print(f"Error adding item at index {idx}: {str(e)}")
            continue

    return {
        "status": "success",
        "total_received": len(items),
        "successfully_uploaded": success_count,
        "duplicates_skipped": duplicate_count
    }


@app.get("/")
async def root():
    return {
        "message": "CRM Message Generator API",
        "version": settings.app_version,
    }
