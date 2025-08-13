from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    source = Column(String)
    publish_date = Column(DateTime)
    content = Column(Text)
    summary = Column(Text)
    keywords = Column(String)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=func.now())

