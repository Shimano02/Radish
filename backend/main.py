import os
import uuid
import logging
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import openai
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment vars from .env
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env vars
DIFY_API_URL = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1").rstrip("/")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "").strip()
GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "")
SHEET_ID = os.getenv("SHEET_ID", "")

# Validate
if not DIFY_API_KEY:
    raise RuntimeError("Missing DIFY_API_KEY in environment")

# CSV configuration
CSV_LOG_DIR = Path("interview_logs")
CSV_LOG_DIR.mkdir(exist_ok=True)

# Video recording configuration
VIDEO_STORAGE_DIR = Path("video_recordings")
VIDEO_STORAGE_DIR.mkdir(exist_ok=True)

# FastAPI setup
app = FastAPI(title="AI Interviewer API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Models
class InterviewerInfo(BaseModel):
    id: str
    name: str
    title: str
    description: str
    image_url: str

class ChatMessage(BaseModel):
    message: str
    interviewer_id: str
    conversation_id: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    stage: int

# CSV utilities
class CSVLogger:
    """CSV面接ログ管理クラス"""
    
    @staticmethod
    def get_csv_file_path() -> Path:
        """日付ベースのCSVファイルパスを取得"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        return CSV_LOG_DIR / f"interview_log_{date_str}.csv"
    
    @staticmethod
    def get_csv_headers() -> List[str]:
        """CSVヘッダーを取得"""
        return [
            "タイムスタンプ", "会話ID", "面接官ID", "面接官名", 
            "ユーザーメッセージ", "AI応答", "対話回数", "ステージ"
        ]
    
    @classmethod
    async def write_interview_log(
        cls,
        conversation_id: str,
        interviewer_id: str,
        interviewer_name: str,
        user_message: str,
        ai_response: str,
        dialogue_count: int,
        stage: int
    ) -> bool:
        """面接ログをCSVファイルに書き込み"""
        try:
            csv_file = cls.get_csv_file_path()
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            write_header = not csv_file.exists()
            
            with open(csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                if write_header:
                    writer.writerow(cls.get_csv_headers())
                
                # データを書き込み
                row_data = [
                    timestamp,
                    conversation_id,
                    interviewer_id,
                    interviewer_name,
                    user_message,
                    ai_response,
                    dialogue_count,
                    stage
                ]
                writer.writerow(row_data)
            
            logger.info(f"面接ログをCSVファイルに保存: {csv_file}")
            return True
            
        except Exception as e:
            logger.error(f"CSVログ保存エラー: {e}")
            return False
    
    @classmethod
    def get_all_interview_records(cls) -> List[Dict[str, Any]]:
        """全ての面接記録を取得"""
        records = []
        
        try:
            for csv_file in CSV_LOG_DIR.glob("interview_log_*.csv"):
                with open(csv_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        record = {
                            "id": f"{row['会話ID']}_{row['対話回数']}",
                            "timestamp": row['タイムスタンプ'],
                            "conversation_id": row['会話ID'],
                            "interviewer_name": row['面接官名'],
                            "user_message": row['ユーザーメッセージ'],
                            "ai_response": row['AI応答'],
                            "dialogue_count": int(row['対話回数']),
                            "stage": int(row['ステージ']),
                            "csv_file": str(csv_file.name)
                        }
                        records.append(record)
        
        except Exception as e:
            logger.error(f"面接記録取得エラー: {e}")
        
        records.sort(key=lambda x: x['timestamp'], reverse=True)
        return records

# OpenAI API utilities
class OpenAIAPIClient:
    """OpenAI API呼び出し管理クラス"""
    
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def send_chat_message(
        self,
        message: str,
        interviewer_id: str,
        conversation_id: str,
        dialogue_count: int,
        dify_conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """OpenAI APIにチャットメッセージを送信"""
        
        if interviewer_id == "data_extractor":
            return await self._extract_structured_data(message)
        
        system_prompt = f"""
あなたは介護施設の面接官「不動」です。施設長として1次面接を担当しています。
応募者との対話回数: {dialogue_count}

以下の特徴で面接を進めてください：
- 親しみやすく、でも真剣な態度
- 介護業界特有の現実的な質問（夜勤、体力的負担、利用者対応など）
- 応募者の経験や人柄を引き出す質問
- 簡潔で分かりやすい日本語

対話が3回以上続いた場合は、面接を自然に終了してください。
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "answer": ai_response,
                "conversation_id": dify_conversation_id or conversation_id,
                "message_id": str(uuid.uuid4())
            }
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise HTTPException(status_code=500, detail="OpenAI API call failed")
    
    async def _extract_structured_data(self, extraction_prompt: str) -> Dict[str, Any]:
        """構造化データ抽出専用メソッド"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "あなたは面接データ抽出の専門家です。与えられた面接会話から正確に情報を抽出し、指定されたJSON形式で回答してください。"
                    },
                    {"role": "user", "content": extraction_prompt}
                ],
                max_tokens=500,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"OpenAI extraction response: {ai_response}")
            
            return {
                "answer": ai_response,
                "message_id": str(uuid.uuid4())
            }
                
        except Exception as e:
            logger.error(f"OpenAI extraction error: {e}")
            return {"answer": "{}", "message_id": str(uuid.uuid4())}

# Session management
class SessionManager:
    """セッション管理クラス"""
    
    def __init__(self):
        self.conversation_sessions: Dict[str, Any] = {}
    
    def create_session(self, interviewer_id: str) -> str:
        """新しいセッションを作成"""
        session_id = str(uuid.uuid4())
        self.conversation_sessions[session_id] = {
            "interviewer_id": interviewer_id,
            "stage": 0,
            "dialogue_count": 0,
            "dify_id": None,
            "messages": [],
            "created_at": datetime.now(timezone.utc)
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """セッションを取得"""
        return self.conversation_sessions.get(session_id)
    
    def update_session(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        dify_conversation_id: Optional[str] = None
    ) -> None:
        """セッションを更新"""
        session = self.conversation_sessions.get(session_id)
        if not session:
            return
        
        session["dialogue_count"] += 1
        session["stage"] += 1
        
        if dify_conversation_id and not session.get("dify_id"):
            session["dify_id"] = dify_conversation_id
        
        timestamp = datetime.now(timezone.utc).isoformat()
        session["messages"].append({
            "user": user_message,
            "ai": ai_response,
            "timestamp": timestamp
        })

# In-memory data
INTERVIEWERS: List[Dict[str, Any]] = [
    {
        "id": "construction_engineer",
        "name": "不動",
        "title": "施設長",
        "description": "１次面接を担当します。",
        #"image_url": "/assets/construction_engineer.png"
        "image_url": "/assets/dayCare.png"
    }

]

class StructuredDataExtractor:
    """構造化データ抽出クラス"""
    
    @staticmethod
    async def extract_interview_data(conversation_history: List[Dict], openai_client: OpenAIAPIClient) -> Dict[str, Any]:
        """面接データから構造化情報を抽出"""
        
        conversation_text = "\n".join([
            f"質問: {msg.get('ai', '')}\n回答: {msg.get('user', '')}" 
            for msg in conversation_history
        ])
        
        extraction_prompt = f"""
以下の面接会話から、応募者の情報を正確に抽出してください。

会話内容:
{conversation_text}

以下のJSON形式で回答してください:
{{
    "name": "応募者の名前（フルネーム）",
    "age": "年齢（数字のみ）",
    "experience": "職歴・経験（具体的な年数と職種）",
    "skills": "スキル・資格",
    "motivation": "志望動機・やる気",
    "communication": "コミュニケーション能力の評価",
    "completeness_score": "情報の完全性（1-10）",
    "quality_score": "回答の質（1-10）",
    "recommendation": "本面接への推薦可否（可/不可）"
}}

情報が不明な場合は"不明"と記載してください。
"""
        
        try:
            response = await openai_client._extract_structured_data(extraction_prompt)
            
            logger.info(f"OpenAI API response: {response}")
            answer = response.get("answer", "{}")
            logger.info(f"Answer field: {answer}")
            
            start_idx = answer.find('{')
            end_idx = answer.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = answer[start_idx:end_idx]
                logger.info(f"Extracted JSON string: {json_str}")
                extracted_data = json.loads(json_str)
            else:
                logger.warning(f"No JSON found in answer: {answer}")
                extracted_data = {}
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"データ抽出エラー: {e}")
            return {}

class GoogleSheetsService:
    """Google Sheets連携サービス"""
    
    @staticmethod
    async def save_interview_data(conversation_id: str, extracted_data: Dict[str, Any]) -> bool:
        """抽出データをGoogle Sheetsに保存"""
        if not GOOGLE_SERVICE_ACCOUNT_PATH or not SHEET_ID:
            logger.warning("Google Sheets設定が不完全です")
            return False
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_SERVICE_ACCOUNT_PATH,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            
            values = [[
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                conversation_id,
                extracted_data.get("name", "不明"),
                extracted_data.get("age", "不明"),
                extracted_data.get("experience", "不明"),
                extracted_data.get("skills", "不明"),
                extracted_data.get("motivation", "不明"),
                extracted_data.get("communication", "不明"),
                extracted_data.get("completeness_score", "0"),
                extracted_data.get("quality_score", "0"),
                extracted_data.get("recommendation", "不可")
            ]]
            
            body = {
                'values': values
            }
            
            result = service.spreadsheets().values().append(
                spreadsheetId=SHEET_ID,
                range='A:K',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"Google Sheets保存成功: {result.get('updates', {}).get('updatedRows', 0)}行追加")
            return True
                
        except Exception as e:
            logger.error(f"Google Sheets保存エラー: {e}")
            return False

class InterviewEvaluator:
    """面接評価クラス"""
    
    @staticmethod
    async def evaluate_interview(messages: List[Dict], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """面接内容を総合評価"""
        try:
            evaluation = {
                "overall_score": 0,
                "communication_score": 0,
                "experience_relevance": 0,
                "motivation_level": 0,
                "response_quality": 0,
                "interview_readiness": "不可",
                "strengths": [],
                "weaknesses": [],
                "recommendations": []
            }
            
            message_count = len(messages)
            if message_count >= 3:
                evaluation["communication_score"] += 3
            if message_count >= 5:
                evaluation["communication_score"] += 2
            
            completeness = 0
            if extracted_data.get("name") and extracted_data.get("name") != "不明":
                completeness += 2
                evaluation["strengths"].append("名前が明確")
            else:
                evaluation["weaknesses"].append("名前が不明確")
                
            if extracted_data.get("age") and extracted_data.get("age") != "不明":
                completeness += 2
                evaluation["strengths"].append("年齢情報あり")
            else:
                evaluation["weaknesses"].append("年齢情報なし")
                
            if extracted_data.get("experience") and extracted_data.get("experience") != "不明":
                completeness += 3
                evaluation["strengths"].append("職歴情報あり")
                exp_text = extracted_data.get("experience", "").lower()
                if any(keyword in exp_text for keyword in ["年", "経験", "勤務"]):
                    evaluation["experience_relevance"] += 3
            else:
                evaluation["weaknesses"].append("職歴情報不足")
            
            total_response_length = sum(len(msg.get('user', '')) for msg in messages)
            if total_response_length > 100:
                evaluation["response_quality"] += 3
                evaluation["strengths"].append("詳細な回答")
            elif total_response_length > 50:
                evaluation["response_quality"] += 2
            else:
                evaluation["weaknesses"].append("回答が簡潔すぎる")
            
            evaluation["overall_score"] = (
                evaluation["communication_score"] + 
                evaluation["experience_relevance"] + 
                evaluation["response_quality"] + 
                completeness
            )
            
            if evaluation["overall_score"] >= 8:
                evaluation["interview_readiness"] = "可"
                evaluation["recommendations"].append("本面接に進行可能")
            elif evaluation["overall_score"] >= 5:
                evaluation["interview_readiness"] = "要検討"
                evaluation["recommendations"].append("追加質問後に判定")
            else:
                evaluation["interview_readiness"] = "不可"
                evaluation["recommendations"].append("基本情報の再確認が必要")
            
            if evaluation["communication_score"] < 3:
                evaluation["recommendations"].append("コミュニケーション能力の向上が必要")
            if evaluation["experience_relevance"] < 2:
                evaluation["recommendations"].append("関連経験の詳細説明が必要")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"面接評価エラー: {e}")
            return {
                "overall_score": 0,
                "interview_readiness": "評価不可",
                "error": str(e)
            }

# Initialize services
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAIAPIClient(OPENAI_API_KEY)
session_manager = SessionManager()

# Helper functions
def get_interviewer_by_id(interviewer_id: str) -> Optional[Dict[str, Any]]:
    """IDから面接官情報を取得"""
    return next((i for i in INTERVIEWERS if i["id"] == interviewer_id), None)

def extract_ai_response(dify_data: Dict[str, Any]) -> str:
    """Dify APIレスポンスからAI応答を抽出"""
    return (
        dify_data.get("answer")
        or dify_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        or "申し訳ございませんが、応答を取得できませんでした。"
    )

# API Endpoints
@app.get("/api/interviewers", response_model=List[InterviewerInfo])
async def get_interviewers():
    """面接官一覧を取得"""
    return INTERVIEWERS

@app.post("/api/chat/start")
async def start_chat(interviewer_id: str):
    """面接チャットを開始"""
    interviewer = get_interviewer_by_id(interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=400, detail="Invalid interviewer ID")
    
    session_id = session_manager.create_session(interviewer_id)
    greeting = "準備ができましたら『開始』を押して下さい。音声でも入力可能です。"
    
    logger.info(f"Started new interview session: {session_id} with {interviewer_id}")
    
    return {
        "conversation_id": session_id,
        "greeting": greeting,
        "interviewer": interviewer
    }

@app.post("/api/chat/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    """メッセージを送信し、AI応答を取得"""
    # 1) セッション確認
    session = session_manager.get_session(chat_message.conversation_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    # 2) 面接官情報取得
    interviewer = get_interviewer_by_id(chat_message.interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=400, detail="Invalid interviewer ID")
    
    openai_response = await openai_client.send_chat_message(
        message=chat_message.message,
        interviewer_id=chat_message.interviewer_id,
        conversation_id=chat_message.conversation_id,
        dialogue_count=session["dialogue_count"] + 1,
        dify_conversation_id=session.get("dify_id")
    )
    
    # 4) AI応答抽出
    ai_response = extract_ai_response(openai_response)
    
    # 5) セッション更新
    session_manager.update_session(
        session_id=chat_message.conversation_id,
        user_message=chat_message.message,
        ai_response=ai_response,
        dify_conversation_id=openai_response.get("conversation_id")
    )
    
    # 6) 更新されたセッション情報を取得
    updated_session = session_manager.get_session(chat_message.conversation_id)
    
    if updated_session:
        await CSVLogger.write_interview_log(
            conversation_id=chat_message.conversation_id,
            interviewer_id=chat_message.interviewer_id,
            interviewer_name=interviewer["name"],
            user_message=chat_message.message,
            ai_response=ai_response,
            dialogue_count=updated_session["dialogue_count"],
            stage=updated_session["stage"]
        )
        
        if updated_session["dialogue_count"] >= 3:
            extracted_data = await StructuredDataExtractor.extract_interview_data(
                updated_session["messages"], openai_client
            )
            
            if extracted_data:
                await GoogleSheetsService.save_interview_data(
                    chat_message.conversation_id, extracted_data
                )
                logger.info(f"構造化データを保存: {extracted_data}")
    
    # 8) レスポンス返却
    return ChatResponse(
        response=ai_response,
        conversation_id=chat_message.conversation_id,
        stage=updated_session["stage"] if updated_session else 1
    )

@app.post("/api/admin/upload-recording")
async def upload_recording(
    conversation_id: str,
    file: UploadFile = File(...)
):
    """録画ファイルをアップロード"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{conversation_id}_{timestamp}.webm"
        file_path = VIDEO_STORAGE_DIR / filename
        
        # ファイルを保存
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"録画ファイルを保存: {file_path}")
        
        return {
            "success": True,
            "filename": filename,
            "file_path": str(file_path)
        }
    
    except Exception as e:
        logger.error(f"録画アップロードエラー: {e}")
        raise HTTPException(status_code=500, detail="録画ファイルのアップロードに失敗しました")

@app.get("/api/admin/records")
async def get_interview_records():
    """面接記録一覧を取得"""
    try:
        records = CSVLogger.get_all_interview_records()
        
        conversation_groups = {}
        for record in records:
            conv_id = record['conversation_id']
            if conv_id not in conversation_groups:
                recording_files = list(VIDEO_STORAGE_DIR.glob(f"{conv_id}_*.webm"))
                has_recording = len(recording_files) > 0
                
                conversation_groups[conv_id] = {
                    "id": conv_id,
                    "timestamp": record['timestamp'],
                    "conversation_id": conv_id,
                    "interviewer_name": record['interviewer_name'],
                    "user_messages": 0,
                    "ai_responses": 0,
                    "duration": "計算中",
                    "has_recording": has_recording,
                    "csv_file": record['csv_file']
                }
            conversation_groups[conv_id]["user_messages"] += 1
            conversation_groups[conv_id]["ai_responses"] += 1
        
        return list(conversation_groups.values())
    
    except Exception as e:
        logger.error(f"面接記録取得エラー: {e}")
        raise HTTPException(status_code=500, detail="面接記録の取得に失敗しました")

@app.get("/api/admin/recording/{record_id}")
async def download_recording(record_id: str):
    """録画ファイルをダウンロード"""
    try:
        recording_files = list(VIDEO_STORAGE_DIR.glob(f"{record_id}_*.webm"))
        
        if not recording_files:
            raise HTTPException(status_code=404, detail="録画ファイルが見つかりません")
        
        recording_file = max(recording_files, key=lambda f: f.stat().st_mtime)
        
        return FileResponse(
            path=str(recording_file),
            filename=f"interview_{record_id}.webm",
            media_type="video/webm"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"録画ダウンロードエラー: {e}")
        raise HTTPException(status_code=500, detail="録画ファイルのダウンロードに失敗しました")

@app.get("/api/admin/csv/{csv_filename}")
async def download_csv(csv_filename: str):
    """CSVファイルをダウンロード"""
    try:
        csv_file_path = CSV_LOG_DIR / csv_filename
        
        if not csv_file_path.exists():
            raise HTTPException(status_code=404, detail="CSVファイルが見つかりません")
        
        return FileResponse(
            path=str(csv_file_path),
            filename=csv_filename,
            media_type="text/csv"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSVダウンロードエラー: {e}")
        raise HTTPException(status_code=500, detail="CSVファイルのダウンロードに失敗しました")

@app.get("/api/admin/extracted-data/{conversation_id}")
async def get_extracted_data(conversation_id: str):
    """抽出された構造化データを取得"""
    try:
        session = session_manager.get_session(conversation_id)
        if not session:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        extracted_data = await StructuredDataExtractor.extract_interview_data(
            session["messages"], openai_client
        )
        
        return {
            "conversation_id": conversation_id,
            "extracted_data": extracted_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"抽出データ取得エラー: {e}")
        raise HTTPException(status_code=500, detail="データ取得に失敗しました")

@app.get("/api/admin/all-extracted-data")
async def get_all_extracted_data():
    """全CSVログから構造化データを抽出・評価"""
    try:
        all_results = []
        
        for csv_file in os.listdir(CSV_LOG_DIR):
            if csv_file.startswith("interview_log_") and csv_file.endswith(".csv"):
                csv_path = os.path.join(CSV_LOG_DIR, csv_file)
                
                conversations = {}
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        conv_id = row['会話ID']
                        if conv_id not in conversations:
                            conversations[conv_id] = {
                                'conversation_id': conv_id,
                                'interviewer_name': row['面接官名'],
                                'start_time': row['タイムスタンプ'],
                                'messages': []
                            }
                        
                        conversations[conv_id]['messages'].append({
                            'user': row['ユーザーメッセージ'],
                            'ai': row['AI応答'],
                            'timestamp': row['タイムスタンプ'],
                            'dialogue_count': int(row['対話回数'])
                        })
                
                for conv_id, conv_data in conversations.items():
                    if len(conv_data['messages']) >= 3:  # 3回以上の対話がある場合のみ
                        extracted_data = await StructuredDataExtractor.extract_interview_data(
                            conv_data['messages'], openai_client
                        )
                        
                        evaluation = await InterviewEvaluator.evaluate_interview(
                            conv_data['messages'], extracted_data
                        )
                        
                        all_results.append({
                            'conversation_id': conv_id,
                            'interviewer_name': conv_data['interviewer_name'],
                            'start_time': conv_data['start_time'],
                            'message_count': len(conv_data['messages']),
                            'extracted_data': extracted_data,
                            'evaluation': evaluation,
                            'csv_file': csv_file
                        })
        
        return {
            "total_interviews": len(all_results),
            "extraction_timestamp": datetime.now().isoformat(),
            "results": all_results
        }
        
    except Exception as e:
        logger.error(f"全データ抽出エラー: {e}")
        raise HTTPException(status_code=500, detail="全データ抽出に失敗しました")

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "csv_log_dir": str(CSV_LOG_DIR.absolute()),
        "video_storage_dir": str(VIDEO_STORAGE_DIR.absolute())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)), 
        reload=True
    )
