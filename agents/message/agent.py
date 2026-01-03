# TODO 1. 메시지 발송 목적 기반 페르소나 선정
# TODO 2. 주요 메시지 성과, 예상 발송일 기반 RAG 조회
# TODO 3. 메시지 생성 Parrell agent
#  - 전략별 Loop agent
#    - 메시지 생성
#    - 생성 메시지 평가

# root_agent
# - sequential agent => 순서대로 agent 동작

# report_agent
# - 최종 결과 작성 == formatting 

# app = App(root_agent=root_agent, name="message")

from google.adk.agents import LlmAgent
from google.adk.apps import App
from .sub_agents.message_generate_pipeline import message_generate_pipeline
from config import config

from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

# TODO 1. user state 체크 후 없다면 적용 로직 추가
def set_state(callback_context: CallbackContext) -> Optional[types.Content]:
    # brand_tone
    brand_tone = "친구 같은 친근한 말투, 유행어 활용, 밝고 경쾌한 대화체"
    # message_purpose
    message_purpose = "고객과의 감성적 연결을 강화하고, 구매 전환을 유도"
    # persona
    persona = """
##  레이지 스킵케어족
뷰티계의 맥가이버로 불리는 레이지 스킵케어족은 실용적 관점을 가지고 있습니다. 셀프케어 등에 사용되는 시간을 절약하고 참신한 아이디어로 새로운 뷰티 콘셉트를 시도합니다 바쁜 생활 속에서도 간편하게 뷰티 루틴을 소화하는 데 적극적이며 완벽주의보다 정신건강에 우선순위를 두는 성향이 있습니다.

- **주요 소비성향**

시간과 돈 수고 등에 대한 부담을 덜어주는 제품을 선호하며 휴식과 웰빙 등에서 소비 동기를 얻습니다.
복잡한 메이크업 백을 기피하며 간단하면서도 기능성이 높은 제품을 선호하며 구독 서비스 및 로컬 배송 서비스로 제품을 구매하는 편입니다.

- **추구하는 뷰티스타일**

뷰티 경험이 풍부한 X세대 및 베이비부머 세대와 일상이 바쁜 Z세대가 주를 이루며 서로의 세대는 다르지만 미니멀리즘, 세련미 등 과도하지 않은 미를 추구하는 공통점이 있습니다. 스킨케어, 화장품이 복합된 하이브리드 제품과 이너뷰티 보충제를 스마트한 뷰티 루팅을 위한 필수품으로 여깁니다.
선호 브랜드는 Ami Cole, INRYU, Crown 등이며 유럽, 미국, 아시아(한국, 일본)을 중심으로 인기를 얻고 있습니다.

- **브랜드 실천전략**
레이지 스킵케어족의 마음을 얻으려면 셀프케어 시간을 줄일 수 있는 실용적이면서도 효과적인 제품을 개발하는 것이 중요합니다.
제품에 대한 객관적인 정보를 중시하므로 과학적인 근거를 제시하되 데이터스모그 현상이 나타나지 않도록 단순 명료하면서 투명하고 정직하게 접근하는 시도가 필요합니다.
"""

    # message_reference [optional]
    callback_context.state["brand_tone"] = brand_tone
    callback_context.state["message_purpose"] = message_purpose
    callback_context.state["persona"] = persona
    return None
   
# TODO : Sequential Agent 로 수정
# TODO 1. 메시지 발송 목적 기반 페르소나 선정 에이전트 추가
# TODO 2. 주요 메시지 성과, 예상 발송일 기반 RAG 조회 에이전트 추가
root_agent = LlmAgent(
    name="message_generator",
    model=config.worker_model,
    description="고객의 요청에 따라 마케팅 메시지를 생성한다.",
    instruction="당신은 고객의 마케팅 메시지 생성 요청에 따라 메시지를 작성하는 전문가입니다. 'message_generate_pipeline' sub agents를 통해 마케팅 메시지를 생성하세요.",
    sub_agents=[message_generate_pipeline],
    before_agent_callback=set_state
)

app = App(root_agent=root_agent, name="message")