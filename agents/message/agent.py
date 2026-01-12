import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))


from datetime import datetime
from google.adk.agents import SequentialAgent
from google.adk.apps import App
from .sub_agents.message_generate_pipeline.agent import message_generate_pipeline_agent
from .sub_agents.performance_estimation.agent import performance_estimation_agent
from .sub_agents.report.agent import report_agent
from .sub_agents.types import MessageType
from .plugins.status_logging import StatusLoggingPlugin

from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional

from agents.service import find_persona_by_id, format_persona

from dotenv import load_dotenv
load_dotenv()


def set_state(callback_context: CallbackContext) -> Optional[types.Content]:
    # TODO: 임시 데이터
    callback_context.state["persona_id"] = "a7f3e9d2-4b8c-4a1f-9e2d-7c5b8a3f1e6d"
    callback_context.state["brand_tone"] = "효과적인 제품 소개"
    callback_context.state["message_purpose"] = "홍보"
    callback_context.state["key_marketing_achievements"] = "판매량 증가"
    callback_context.state["message_sending_datetime"] = datetime(2026, 1, 1, 20, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    callback_context.state["product_info"] = "이니스프리 미스트: 20ml, 피부 진정 효과"
    callback_context.state["current_event_info"] = "2026년 1월 1일 신제품 출시"
    callback_context.state["additional_request"] = "None"
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

    return None


def set_output(callback_context: CallbackContext) -> types.Content:
    output = {
        message_type.value: callback_context.state.get(f"{message_type.value}_final_report")
        for message_type in MessageType
    }
    
    return types.Content(
        parts=[types.Part(text=json.dumps(output, ensure_ascii=False))],
        role="model",
    )
   
root_agent = SequentialAgent(
    name="main_message_generator",
    description="고객의 요청에 따라 마케팅 메시지를 생성한다.",
    sub_agents=[
        message_generate_pipeline_agent,
        performance_estimation_agent,
        report_agent
    ],
    before_agent_callback=set_state,
    after_agent_callback=set_output
)

app = App(
    root_agent=root_agent, 
    name="message",
    plugins=[
        StatusLoggingPlugin()
    ]
)

def get_app_name() -> str:
    return "message"