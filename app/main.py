from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database.database import engine, Base
from app.api.endpoints import news, chat
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI News Chatbot",
    description="A chatbot for querying AI and tech news.",
    version="1.0.0"
)

# CORS Ayarları
origins = [
    "http://localhost",
    "http://localhost:3000", # React development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router'ları
app.include_router(news.router, prefix="/api/v1", tags=["news"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

# React Frontend'ini Sunma
# Bu bölüm, projenin build edilmiş halini sunmak içindir.
# 'frontend/build' klasörünün varlığını kontrol eder.
if os.path.exists("frontend/build"):
    app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI News Chatbot API"}

