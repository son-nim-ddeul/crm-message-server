from holidayskr import year_holidays
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta


class MessageReferenceBase(BaseModel):
    title: str
    content: str
    category: str | None = None


class MessageReferenceCreate(MessageReferenceBase):
    pass


class MessageReferenceResponse(MessageReferenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime



class EventContent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str | None = None
    parts: list | None = None


class EventError(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    error_code: str | None = None
    error_message: str | None = None


class EventResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    event_status: str
    user_id: str
    session_id: str
    branch: str | None = None
    author: str | None = None
    timestamp: float
    is_final_response: bool | None = None
    ui_status: str | None = None # TODO: state_delta.ui_status
    content: EventContent | None = None
    error: EventError | None = None
    
class AgentRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str
    session_id: str | None = None

class MessageAgentConfig(BaseModel):
    brand_tone: str                                     # 브랜드의 톤
    message_purpose: str                                # 메시지의 목적 (정보 전달, 홍보, 행동 유도 등)
    persona_id: str                                     # 타겟 페르소나 ID
    key_marketing_achievements: str | None = None       # 주요 마케팅 성과 (예: 판매량 증가, 회원 유지율 상승 등)
    message_sending_datetime: datetime | None = None    # 메시지 발송 시간 (예: 2026-01-06 18:00:00)
    product_info: str | None = None                     # 제품/서비스 정보 (예: 제품 이름, 가격, 특징 등)
    current_event_info: str | None = None               # 현재 이벤트 정보 (예: 신제품 출시, 이벤트 진행 중 등)
    additional_request: str | None = None               # 추가 요청 사항


    def metadata_dict(self) -> dict:
        return {
            "brand_tone": self.brand_tone,
            "message_purpose": self.message_purpose,
            "key_marketing_achievements": self.key_marketing_achievements,
            "message_sending_datetime": self.message_sending_datetime.strftime("%Y-%m-%d %H:%M:%S") if self.message_sending_datetime else None,
            "product_info": self.product_info,
            "holidays": self._get_holidays(),
            "season": self._get_season(),
        }
    
    @property
    def is_sending_datetime_set(self) -> bool:
        return self.message_sending_datetime is not None
    
    def _get_season(self) -> str:
        def check_season(month: int) -> str:
            if month in {12, 1, 2}:
                return "겨울"
            elif month in {3, 4, 5}:
                return "봄"
            elif month in {6, 7, 8}:
                return "여름"
            elif month in {9, 10, 11}:
                return "가을"
            else:
                raise ValueError(f"Invalid month: {month}")

        date_formatted = self.message_sending_datetime.strftime("%Y-%m-%d")
        season = check_season(self.message_sending_datetime.month)
        return f"{date_formatted} {season}"


    def _get_holidays(self) -> list[str]:
        start_date = self.message_sending_datetime
        end_date = self.message_sending_datetime + timedelta(days=14)
        holidays_info = []

        for year in range(start_date.year, end_date.year + 1):
            holidays_info += [
                f"{hol_date.strftime('%Y-%m-%d')} {hol_name}".strip()
                for hol_date, hol_name in year_holidays(str(year))
            ]

        return holidays_info


class MessageAgentRequest(AgentRequest):
    config: MessageAgentConfig
