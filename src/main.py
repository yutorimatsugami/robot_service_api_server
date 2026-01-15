import warnings
# Suppress specific FutureWarnings to keep logs clean
warnings.filterwarnings("ignore", message=".*You are using a Python version.*")
warnings.filterwarnings("ignore", message=".*All support for the `google.generativeai` package has ended.*")

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uvicorn

import models, schemas, crud, database, gemini_client

# Create tables if not exist (simple migration)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Robot Service API")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Robot Service API is running"}

@app.get("/ads", response_model=List[schemas.AdContent])
def read_ads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ads = crud.get_ads(db, skip=skip, limit=limit)
    return ads

@app.post("/chat", response_model=schemas.ChatResponse)
def chat_with_robot(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    user_msg = request.message
    
    # 1. Check FAQ (Simple Keyword Match)
    faq = crud.get_faq_response(db, user_msg)
    if faq:
        return schemas.ChatResponse(response=faq.response_text)
    
    # 2. RAG with Gemini
    # Retrieve relevant context (For simplicity, we dump all ads info or search)
    # Ideally, use vector search. Here we do simple keyword search or just dump all if small.
    # Let's search ads that might be relevant to the message keywords?
    # Or just provide all ad info as context because the dataset is small.
    context_text = crud.get_all_ads_text(db)
    
    ai_response = gemini_client.generate_chat_response(user_msg, context=context_text)
    
    return schemas.ChatResponse(response=ai_response)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
