import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.inference import MiniMindEngine

app = FastAPI(title="MiniMind API", version="1.0")
engine = None

@app.on_event("startup")
def startup_event():
    global engine
    engine = MiniMindEngine()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    max_tokens: int = 150
    temperature: float = 0.7

@app.post("/chat")
def chat(request: ChatRequest):
    if engine is None:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    formatted_messages = [{"role": m.role, "content": m.content} for m in request.messages]
    reply = engine.generate(
        messages=formatted_messages,
        max_new_tokens=request.max_tokens,
        temperature=request.temperature
    )
    return {"reply": reply}

# run comment: uvicorn app.api:app --host 0.0.0.0 --port 8000