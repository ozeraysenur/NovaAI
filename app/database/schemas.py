from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArticleBase(BaseModel):
    title: str
    url: str
    source: str
    publish_date: Optional[datetime] = None
    content: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int
    summary: Optional[str] = None
    keywords: Optional[str] = None

    class Config:
        orm_mode = True

class ChatHistoryBase(BaseModel):
    user_id: str
    query: str
    response: str

class ChatHistoryCreate(ChatHistoryBase):
    pass

class ChatHistory(ChatHistoryBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class ChatQuery(BaseModel):
    user_id: str
    query: str


