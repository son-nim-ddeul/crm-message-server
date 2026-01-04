import logging
from datetime import datetime
from enum import StrEnum
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

class EventStatus(StrEnum):
    START = "start"
    PROGRESS = "progress"
    COMPLETE = "complete"
    ERROR = "error"

def __get_app(app_name: str) -> App:
    if app_name == message_app.name:
        return message_app
    else:
        raise Exception("지원되지 않는 adk app_name입니다.")


def initialize_adk_services():
    """ADK 서비스 초기화 (FastAPI lifespan에서 호출)"""
    global _session_service, _runners
    
    # SessionService 초기화
    _session_service = SqliteSessionService(
        db_path=settings.rds_db_path
    )
    
    # Runner 초기화
    app = __get_app(message_app.name)
    _runners[message_app.name] = Runner(
        app=app,
        session_service=_session_service
    )


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
    
def json_dumps(response: schemas.EventResponse) -> str:
    json_str = response.model_dump_json()
    return f"data: {json_str}\n\n"
    
async def execute_agent(
    user_id: str, 
    session_id: str, 
    runner: Runner
) -> AsyncGenerator[str, None]:
    # TODO: 에이전트 new_message 수정
    execute_message = Content(
        parts=[Part(text="마케팅 메시지 생성해줘.")]
    )
    try:
        # Stream 시작 yield
        start_response = schemas.EventResponse(
            event_status=EventStatus.START,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now().timestamp()
        )
        yield json_dumps(start_response)
        
        async with Aclosing(
            runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=execute_message
            )
        ) as agen:
            async for event in agen:
                ui_status = event.actions.state_delta.get("ui_status")
                response = schemas.EventResponse(
                    event_status=EventStatus.PROGRESS,
                    user_id=user_id,
                    session_id=session_id,
                    branch=event.branch,
                    author=event.author,
                    timestamp=event.timestamp,
                    is_final_response=event.is_final_response(),
                    ui_status=ui_status
                )
                
                if event.error_code is not None:
                    response.error=schemas.EventError(
                        error_code=event.error_code,
                        error_message=event.error_message
                    )
                
                if event.content is not None:
                    response.content=schemas.EventContent(
                        role=event.content.role,
                        parts=event.content.parts
                    )
                
                yield json_dumps(response)
                
            # Stream 종료 yield
            complete_response = schemas.EventResponse(
                event_status=EventStatus.COMPLETE,
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now().timestamp()
            )
            yield json_dumps(complete_response)
    except Exception as e:
        logger.exception("Error in execute_agent: %s", e)
        response = schemas.EventResponse(
            event_status=EventStatus.ERROR,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now().timestamp()
        )

        if str(e) is None:
            error_message="에이전트 동작간 예외가 발생하였습니다."
        else:
            error_message=str(e)
            
        response.error = schemas.EventError(
            error_code="INTERNAL_ERROR",
            error_message=error_message
        )
        
        yield json_dumps(response)