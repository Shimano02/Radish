from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import json
import os
from datetime import datetime
import uuid

app = FastAPI(title="AI Interviewer API")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class InterviewerInfo(BaseModel):
    id: str
    name: str
    title: str
    description: str
    image_url: str

class ChatMessage(BaseModel):
    message: str
    interviewer_id: str
    conversation_id: str = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    stage: int

INTERVIEWERS = [
    {
        "id": "construction_engineer",
        "name": "美咲",
        "title": "建設エンジニア",
        "description": "技術面接を担当します。建設業界での経験や技術スキルについてお聞きします。",
        "image_url": "/assets/construction_engineer.png"
    },
    {
        "id": "hr_manager", 
        "name": "雅美",
        "title": "人事担当",
        "description": "人事面接を担当します。あなたの経歴や志望動機についてお聞きします。",
        "image_url": "/assets/hr_manager.png"
    },
    {
        "id": "restaurant_manager",
        "name": "さくら", 
        "title": "レストラン店長",
        "description": "サービス面接を担当します。接客経験やコミュニケーション能力についてお聞きします。",
        "image_url": "/assets/restaurant_manager.png"
    }
]

DIFY_API_URL = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
GOOGLE_SHEETS_TOKEN = os.getenv("GOOGLE_SHEETS_TOKEN", "")

conversation_sessions = {}

@app.get("/api/interviewers", response_model=List[InterviewerInfo])
async def get_interviewers():
    return INTERVIEWERS

@app.post("/api/chat/start")
async def start_chat(interviewer_id: str):
    conversation_id = str(uuid.uuid4())
    conversation_sessions[conversation_id] = {
        "interviewer_id": interviewer_id,
        "stage": 0,
        "dialogue_count": 0,
        "messages": []
    }
    
    greeting_message = "映像と音声、問題ありませんか？\n準備ができましたら「開始」と入力して下さい。"
    
    return {
        "conversation_id": conversation_id,
        "greeting": greeting_message,
        "interviewer": next(i for i in INTERVIEWERS if i["id"] == interviewer_id)
    }

@app.post("/api/chat/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    if not chat_message.conversation_id or chat_message.conversation_id not in conversation_sessions:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    session = conversation_sessions[chat_message.conversation_id]
    session["dialogue_count"] += 1
    
    mock_responses = {
        1: "こんにちは！面接を始めさせていただきます。まず、簡単に自己紹介をお願いします。お名前と今までの経験について教えてください。",
        2: "ありがとうございます。建設業界での具体的な経験やスキルについて詳しく教えてください。どのようなプロジェクトに携わったことがありますか？",
        3: "素晴らしい経験をお持ちですね。なぜ弊社を志望されたのか、そして将来のキャリア目標について教えてください。",
        4: "本日は貴重なお時間をいただき、ありがとうございました。面接は以上で終了です。結果については後日ご連絡いたします。"
    }
    
    if session["dialogue_count"] <= 4:
        ai_response = mock_responses.get(session["dialogue_count"], "ご質問ありがとうございます。詳しく教えてください。")
        session["stage"] = min(session["dialogue_count"], 4)
    else:
        ai_response = "面接は終了しました。ありがとうございました。"
        session["stage"] = 4
    
    if DIFY_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                dify_response = await client.post(
                    f"{DIFY_API_URL}/chat-messages",
                    headers={
                        "Authorization": f"Bearer {DIFY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "inputs": {
                            "user_message": chat_message.message,
                            "interviewer_type": session["interviewer_id"],
                            "dialogue_count": session["dialogue_count"]
                        },
                        "query": chat_message.message,
                        "response_mode": "blocking",
                        "conversation_id": chat_message.conversation_id,
                        "user": "user"
                    }
                )
                
                if dify_response.status_code == 200:
                    dify_data = dify_response.json()
                    ai_response = dify_data.get("answer", ai_response)
        except Exception as e:
            print(f"Dify API error: {e}")
    
    session["messages"].append({
        "user": chat_message.message,
        "ai": ai_response,
        "timestamp": datetime.now().isoformat()
    })
    
    await record_to_sheets(chat_message.conversation_id, chat_message.message, ai_response, session)
    
    return ChatResponse(
        response=ai_response,
        conversation_id=chat_message.conversation_id,
        stage=session["stage"]
    )

async def record_to_sheets(conversation_id: str, user_message: str, ai_response: str, session: Dict[str, Any]):
    if not GOOGLE_SHEETS_TOKEN:
        return
    
    try:
        async with httpx.AsyncClient() as client:
            sheets_data = {
                "values": [[
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    conversation_id,
                    str(session["dialogue_count"]),
                    "面接官",
                    session["interviewer_id"],
                    user_message,
                    ai_response
                ]]
            }
            
            await client.post(
                "https://sheets.googleapis.com/v4/spreadsheets/1OLFQ7PW4j6Lm8E46nZ6KjiEBIKBMUAaZt-a4LfARKPk/values/Sheet1:append?valueInputOption=USER_ENTERED",
                headers={
                    "Authorization": f"Bearer {GOOGLE_SHEETS_TOKEN}",
                    "Content-Type": "application/json"
                },
                json=sheets_data
            )
    except Exception as e:
        print(f"Failed to record to sheets: {e}")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
