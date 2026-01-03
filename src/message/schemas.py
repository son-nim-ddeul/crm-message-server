from pydantic import BaseModel
from datetime import datetime


class MessageReferenceBase(BaseModel):
    title: str
    content: str
    category: str | None = None


class MessageReferenceCreate(MessageReferenceBase):
    pass


class MessageReferenceResponse(MessageReferenceBase):
    id: int
    created_at: datetime

    class ConfigDict:
        from_attributes = True
