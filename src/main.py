from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # (필요시) 시작 시 실행할 코드
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


@app.get("/")
async def root():
    return {
        "message": "CRM Message Generator API",
        "version": settings.app_version,
    }
