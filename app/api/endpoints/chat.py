from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services import chat_service
from app.database import database, schemas

router = APIRouter()

@router.post("/chat", response_model=schemas.ChatHistoryBase)
async def chat_with_agent(query: schemas.ChatQuery):
    """
    Handles a user's query by passing it to the chat agent.
    It takes a user_id for session management and a query.
    """
    if not query.query or not query.user_id:
        raise HTTPException(status_code=400, detail="Query and user_id cannot be empty.")
        
    response_text = await chat_service.run_chat_logic(query=query.query, user_id=query.user_id)
    
    # Dönen yanıtı schema'ya uygun hale getir
    response_data = schemas.ChatHistoryBase(
        user_id=query.user_id,
        query=query.query,
        response=response_text
    )
    
    return response_data

