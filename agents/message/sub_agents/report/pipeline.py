from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

from ..types import MessageType
from agents.config import config
from .prompt import get_report_config
from google.adk.agents.callback_context import CallbackContext


class ReportOutput(BaseModel):
    """Output schema for messages report."""

    estimation: str = Field(
        description="메시지 평가결과를 마크다운 형식의 보고서를 작성한 결과."
    )

    conclusion: str = Field(
        description="생성된 메시지와 메시지 평과 결과를 바탕으로 마크다운 형식의 보고서를 작성한 결과."
    )
    

def save_report_data(callback_context: CallbackContext):
    agent_name = callback_context.agent_name
    message_type = MessageType.get_message_type(agent_name=agent_name)
    
    generated_message = callback_context.state.get(f"{message_type.value}_message")
    report = callback_context.state.get(f"{message_type.value}_report")

    callback_context.state[f"{message_type.value}_final_report"] = {
        "title": generated_message.get("title"),
        "content": generated_message.get("content"),
        "estimation": report.get("estimation"),
        "conclusion": report.get("conclusion"),
    }


def create_report_pipeline(message_type: MessageType, description: str) -> LlmAgent:
    return LlmAgent(
        name=f"{message_type.value}_report_agent",
        model=config.writer_model,
        description=description,
        instruction=get_report_config(message_type=message_type),
        output_schema=ReportOutput,
        output_key=f"{message_type.value}_report",
        after_agent_callback=save_report_data
    )
    
aspirational_dreamer_report = create_report_pipeline(
    message_type=MessageType.ASPIRATIONAL_DREAMER,
    description="generate marketing report of aspirational dreamer message"
)

empathetic_supporter_report = create_report_pipeline(
    message_type=MessageType.EMPATHETIC_SUPPORTER,
    description="generate marketing report of empathetic supporter message"
)

playful_entertainer_report = create_report_pipeline(
    message_type=MessageType.PLAYFUL_ENTERTAINER,
    description="generate marketing report of playful entertainer message"
)

rational_advisor_report = create_report_pipeline(
    message_type=MessageType.RATIONAL_ADVISOR,
    description="generate marketing report of rational advisor message"
)