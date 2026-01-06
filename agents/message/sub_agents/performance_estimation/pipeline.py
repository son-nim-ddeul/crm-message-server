from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from ..types import MessageType
from agents.config import config
from .prompt import get_performance_estimation_config
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional

class PerformanceMetrics(BaseModel):
    cpc: float = Field(description="예상 클릭당 비용(Cost Per Click)")
    roas: float = Field(description="예상 광고 수익률(Return On Ad Spend)")
    cpm: float = Field(description="예상 1,000회 노출당 비용(Cost Per Mille)")
    ctr: float = Field(description="예상 클릭률(Click Through Rate)")

class EstimationOutput(BaseModel):
    """Output schema for messages estimation."""

    previous_date_context_analysis: str = Field(
        description="과거 메시지들이 발송된 날짜, 요일, 시즌성, 이벤트 여부 등 발송 환경을 정리하고 성과와의 연관성을 분석한다."
    )

    pervious_marketing_performance_analysis: str = Field(
        description="과거 메시지들의 CPC, ROAS, CPM, CTR 성과를 분석하고 성과 차이가 발생한 원인을 해석한다."
    )

    predicted_performance_metrics: PerformanceMetrics = Field(
        description="현재 생성된 메시지의 예상 마케팅 성과 지표(CPC, ROAS, CPM, CTR)를 수치로 예측한다."
    )

    message_performance_prediction: str = Field(
        description=(
            "예상 성과 지표(CPC, ROAS, CPM, CTR)를 이렇게 예측한 이유를 설명한다. "
            "과거 성과, 발송 시점 맥락, 메시지 콘텐츠 특징 등을 근거로 논리적으로 서술한다."
        )
    )

    improvement_suggestions: str = Field(
        description="과거 메시지 성과와 예측 결과를 바탕으로 성과 개선을 위한 구체적인 개선 포인트를 제안한다."
    )
    

def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    # {message_type}_previous_message <- RAG 기반
    # TOP-K -> 3건
    
    # distance : 유사도
    # content : 메시지 내용
    # metadata
    #  - CPC, ROAS, CPM, CTR => KPI {CPC, ROAS, CPM, CTR}
    #  - 발송 일자 -> #  => 발송 일자 날짜, 근접 공휴일 (전후 2주 holiday name list), 계절(봄, 여름, 가을, 겨울) 데이터 조회 Tool 추가
    #  => DataContext {...}
    
    
    # TODO: message_sending_datetime state에서 잡아서 구체화 및 없다면 미정이라고 적어야함
    # callback_context.state.get("")
    # callback_context.state[""]
    pass

def create_estimate_pipeline(
    message_type: MessageType, 
    description: str
) -> LlmAgent:
    return LlmAgent(
        name=f"{message_type.value}_estimation_agent",
        model=config.writer_model,
        description=description,
        instruction=get_performance_estimation_config(message_type=message_type),
        output_schema=EstimationOutput,
        output_key=f"{message_type.value}_estimation",
        before_agent_callback=before_agent_callback
    )

aspirational_dreamer_estimation = create_estimate_pipeline(
    message_type=MessageType.ASPIRATIONAL_DREAMER,
    description="generate marketing estimation of aspirational dreamer message"
)

empathetic_supporter_estimation = create_estimate_pipeline(
    message_type=MessageType.EMPATHETIC_SUPPORTER,
    description="generate marketing estimation of empathetic supporter message"
)

playful_entertainer_estimation = create_estimate_pipeline(
    message_type=MessageType.PLAYFUL_ENTERTAINER,
    description="generate marketing estimation of playful entertainer message"
)

rational_advisor_estimation = create_estimate_pipeline(
    message_type=MessageType.RATIONAL_ADVISOR,
    description="generate marketing estimation of rational advisor message"
)
