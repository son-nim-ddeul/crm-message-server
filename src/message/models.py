from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from src.database.session import Base


class MessageReference(Base):
    __tablename__ = "message_references"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category = Column(String)
    created_at = Column(DateTime, server_default=func.now())
