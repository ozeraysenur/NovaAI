from sqlalchemy.orm import Session
from app.database import models, schemas

def create_chat_history(db: Session, history: schemas.ChatHistoryCreate):
    db_history = models.ChatHistory(
        user_id=history.user_id,
        query=history.query,
        response=history.response
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_chat_history_by_user(db: Session, user_id: str, limit: int = 10):
    return db.query(models.ChatHistory).filter(models.ChatHistory.user_id == user_id).order_by(models.ChatHistory.timestamp.desc()).limit(limit).all()

