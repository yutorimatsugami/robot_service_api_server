import warnings
# Suppress specific FutureWarnings to keep logs clean
warnings.filterwarnings("ignore", message=".*You are using a Python version.*")
warnings.filterwarnings("ignore", message=".*All support for the `google.generativeai` package has ended.*")

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uvicorn

import models, schemas, crud, database, gemini_client

# Create tables if not exist (simple migration)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Robot Service API")

# IPアドレスを自動取得してCORS許可リストに追加
import socket
def get_ip_address():
    try:
        # ダミーの接続で自身のIPを取得（外部には接続しない）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

current_ip = get_ip_address()
print(f"🚀 Server IP: {current_ip}")

# CORS設定
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost:1880",
    "https://localhost:1880",
    f"http://{current_ip}:1880",
    f"https://{current_ip}:1880",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.post("/voice_chat", response_model=schemas.ChatResponse)
async def voice_chat_with_robot(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """音声ファイルを受け取り、音声認識してチャット応答を返す"""
    import tempfile
    import os
    
    # 一時ファイルに保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # 1. 音声をテキストに変換
        transcribed_text = gemini_client.voice_to_text(tmp_path)
        
        if transcribed_text.startswith("Error"):
            return schemas.ChatResponse(response=transcribed_text)
        
        # 2. FAQ検索
        faq = crud.get_faq_response(db, transcribed_text)
        if faq:
            return schemas.ChatResponse(response=faq.response_text)
        
        # 3. Gemini RAG
        context_text = crud.get_all_ads_text(db)
        ai_response = gemini_client.generate_chat_response(transcribed_text, context=context_text)
        
        return schemas.ChatResponse(response=ai_response)
    finally:
        # 一時ファイルを削除
        os.unlink(tmp_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
