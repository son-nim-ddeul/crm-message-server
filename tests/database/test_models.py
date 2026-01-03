from sqlalchemy import Column, Integer, String
from src.database.session import Base

class MockItem(Base):
    __tablename__ = "test_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)

