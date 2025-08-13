import asyncio
from langchain.tools import tool
from sqlalchemy.orm import Session
from app.crud import article_crud
from app.database.database import get_db
from app.database.models import Article  # Article modelini import et
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from app.core.config import OPENAI_API_KEY
import logging
from datetime import datetime, timedelta
from typing import List
from langchain.pydantic_v1 import BaseModel, Field

# Logger'ı ayarla
logger = logging.getLogger(__name__)

def get_llm():
    """LLM modelini başlatır."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY ortam değişkeni ayarlanmadı.")
    return ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.3)

async def generate_summary_on_the_fly(article_content: str) -> str:
    """Verilen makale metni için anında bir özet oluşturur."""
    if not article_content:
        return "Özet üretmek için yeterli içerik bulunamadı."
        
    logger.info("Anlık özet üretiliyor...")
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(
        "Aşağıdaki makale metnini analiz et ve yaklaşık 50-75 kelimelik kısa ve öz bir özetini **tamamen Türkçe** olarak yaz.\n\n"
        "--- MAKALe METNİ ---\n{text}"
    )
    chain = prompt | llm | StrOutputParser()
    try:
        summary = await chain.ainvoke({"text": article_content})
        logger.info("Anlık özet başarıyla üretildi.")
        return summary
    except Exception as e:
        logger.error(f"Anlık özet üretimi sırasında hata: {e}")
        return "Özet üretilirken bir hata oluştu."

async def enrich_articles_with_summaries(articles: List[Article]) -> List[Article]:
    """
    Makale listesini alır, eksik özetleri asenkron olarak üretir
    ve makale nesnelerini güncelleyerek geri döndürür.
    """
    tasks = []
    articles_to_process = []
    
    for article in articles:
        if not article.summary or len(article.summary.strip()) < 20:
            articles_to_process.append(article)
            tasks.append(generate_summary_on_the_fly(article.content))

    if tasks:
        generated_summaries = await asyncio.gather(*tasks)
        for i, article in enumerate(articles_to_process):
            article.summary = generated_summaries[i]
            
    return articles

class GetRecentNewsInput(BaseModel):
    days_ago: int = Field(description="Number of days to look back for recent news. Should be an integer.")

@tool("get_recent_news", args_schema=GetRecentNewsInput)
async def get_recent_news(days_ago: int) -> List[Article]:
    """Fetches the top 8 recent news articles from the database based on the number of days ago."""
    db: Session = next(get_db())
    try:
        articles = article_crud.get_recent_articles(db, days_ago=days_ago, limit=8)
        if not articles:
            return []
        return await enrich_articles_with_summaries(articles)
    finally:
        db.close()

class SearchNewsInput(BaseModel):
    topic: str = Field(description="The topic to search for in news articles. e.g., 'GPT-5', 'NVIDIA'")

@tool("search_news_by_topic", args_schema=SearchNewsInput)
async def search_news_by_topic(topic: str) -> List[Article]:
    """Searches for the top 8 relevant news articles by a specific topic."""
    db: Session = next(get_db())
    try:
        articles = article_crud.search_articles_by_topic(db, topic=topic, limit=8)
        if not articles:
            return []
        return await enrich_articles_with_summaries(articles)
    finally:
        db.close()

