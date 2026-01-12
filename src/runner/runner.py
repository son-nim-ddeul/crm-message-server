import logging
from datetime import datetime
from typing import Any
from typing import AsyncGenerator

from google.adk.utils.context_utils import Aclosing
from google.adk.runners import Runner
from google.adk.apps import App
from google.genai.types import Content, Part
from google.adk.sessions.sqlite_session_service import SqliteSessionService
from src.config import settings
from agents.message.agent import app as message_app
from src.message import schemas

logger = logging.getLogger(__name__)

_runners: dict[str, Runner] = {}
_session_service: SqliteSessionService | None = None

def __get_app(app_name: str) -> App:
    if app_name == message_app.name:
        return message_app
    else:
        raise Exception("지원되지 않는 adk app_name입니다.")


def initialize_adk_services():
    """ADK 서비스 초기화 (FastAPI lifespan에서 호출)"""
    global _session_service, _runners
    
    # SessionService 초기화
    _session_service = SqliteSessionService(db_path=settings.rds_db_path)
    
    # Runner 초기화
    app = __get_app(message_app.name)
    _runners[message_app.name] = Runner(app=app, session_service=_session_service)


def get_session_service() -> SqliteSessionService:
    """SessionService 싱글턴 가져오기"""
    if _session_service is None:
        raise RuntimeError("SessionService not initialized. Call initialize_adk_services() first.")
    return _session_service


def get_runner(app_name: str) -> Runner:
    """Runner 싱글턴 가져오기"""
    if app_name not in _runners:
        raise ValueError(f"지원되지 않는 app_name: {app_name}")
    return _runners[app_name]


async def setup_session_and_runner(
    app_name: str,
    user_id: str,
    session_id: str | None = None,
    state_config: dict[str, Any] = {}
) -> tuple[str, Runner]:
    """
    세션과 Runner를 설정합니다.
    Runner는 캐싱된 싱글턴을 사용합니다.
    """
    session_service = get_session_service()
    runner = get_runner(app_name)
    
    if not session_id:
        session = await session_service.create_session(
            app_name=app_name,
            state=state_config,
            user_id=user_id
        )
    else:
        session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        if not session:
            raise Exception(f"세션을 찾을 수 없습니다. session_id={session_id}")
    
    return session.id, runner


async def execute_agent(user_id: str, session_id: str, runner: Runner) -> AsyncGenerator[str, None]:
    # TODO: 에이전트 new_message 수정
    execute_message = Content(parts=[Part(text="마케팅 메시지 생성해줘.")])
    try:
        last_response = schemas.EventResponse.initiate_event_response(user_id=user_id, session_id=session_id)

        async with Aclosing(runner.run_async(user_id=user_id, session_id=session_id, new_message=execute_message)) as agen:
            async for event in agen:
                yield last_response.model_dump_json(ensure_ascii=False)
                last_response = schemas.EventResponse.from_event(user_id=user_id, session_id=session_id, event=event)

        last_response.mark_up_status(status=schemas.EventStatus.COMPLETE)
        yield last_response.model_dump_json(ensure_ascii=False)
        
    except Exception as e:
        logger.exception("Error in execute_agent: %s", e)
        error_message = str(e) if str(e) else "에이전트 동작간 예외가 발생하였습니다."

        response = schemas.EventResponse.from_error_event(
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now().timestamp(),
            error_code="INTERNAL_ERROR",
            error_message=error_message
        )

        yield response.model_dump_json(ensure_ascii=False)
