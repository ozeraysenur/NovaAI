from sqlalchemy.orm import Session
from app.database import models
from app.database.schemas import ArticleCreate
from datetime import datetime

def get_article_by_url(db: Session, url: str):
    return db.query(models.Article).filter(models.Article.url == url).first()

def create_article(db: Session, article: ArticleCreate):
    db_article = models.Article(
        title=article.title,
        url=article.url,
        source=article.source,
        publish_date=article.publish_date,
        content=article.content,
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update_article_summary_and_keywords(db: Session, article_id: int, summary: str, keywords: str):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if db_article:
        db_article.summary = summary
        db_article.keywords = keywords
        db.commit()
        db.refresh(db_article)
    return db_article

def get_recent_articles(db: Session, days_ago: int, limit: int = 8):
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days_ago)
    return db.query(models.Article).filter(models.Article.publish_date >= cutoff_date).order_by(models.Article.publish_date.desc()).limit(limit).all()

def search_articles_by_topic(db: Session, topic: str, limit: int = 8):
    search = f"%{topic}%"
    return db.query(models.Article).filter(
        (models.Article.title.like(search)) |
        (models.Article.keywords.like(search)) |
        (models.Article.summary.like(search))
    ).order_by(models.Article.publish_date.desc()).limit(limit).all()

