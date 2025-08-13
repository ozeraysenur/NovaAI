from fastapi import APIRouter, BackgroundTasks
from app.services import ingestion_service

router = APIRouter()

@router.post("/ingest-news", status_code=202)
async def ingest_news_endpoint(background_tasks: BackgroundTasks):
    """
    Starts a background task to ingest news from all RSS sources.
    """
    background_tasks.add_task(ingestion_service.ingest_news)
    return {"message": "News ingestion started in the background."}


