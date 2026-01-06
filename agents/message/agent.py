from google.adk.agents import SequentialAgent
from google.adk.apps import App
from .sub_agents.message_generate_pipeline.agent import message_generate_pipeline_agent
from .sub_agents.performance_estimation.agent import performance_estimation_agent
from .sub_agents.report.agent import report_agent
from agents.config import config

from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional

from agents.service import find_persona_by_id, format_persona

from dotenv import load_dotenv
load_dotenv()


def set_state(callback_context: CallbackContext) -> Optional[types.Content]:
    persona_id = callback_context.state.get("persona_id")
    if persona_id is None:
        callback_context.state["persona"] = "target persona is None"
        return None
    
    persona = find_persona_by_id(persona_id=persona_id)
    if persona is None:
        callback_context.state["persona"] = "target persona is None"
        return None
    
    formatted_persona = format_persona(persona=persona)
    callback_context.state["persona"] = formatted_persona

    # TODO : key_marketing_achievements state 사용 부분

    return None
   
# TODO 1. Sequential Agent 로 수정
# TODO 2. 주요 메시지 성과, 예상 발송일 기반 RAG 조회 에이전트 추가
root_agent = SequentialAgent(
    name="message_generator",
    description="고객의 요청에 따라 마케팅 메시지를 생성한다.",
    sub_agents=[
        message_generate_pipeline_agent,
        performance_estimation_agent,
        # report_agent
    ],
    before_agent_callback=set_state
)

app = App(root_agent=root_agent, name="message")

def get_app_name() -> str:
    return "message"