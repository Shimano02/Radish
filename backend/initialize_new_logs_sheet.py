#!/usr/bin/env python3
"""
Initialize the new logs sheet with proper headers
"""
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "")
SHEET_ID = "1-q239hLHhHydeFfd4mE-c9xhOfznlvAaYtp_X5Yx3fg"

def initialize_logs_sheet():
    """logsシートにヘッダーを設定"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        headers = [
            "Timestamp",
            "Conversation_ID",
            "Question",
            "Answer",
            "Evaluation",
            "Name",
            "Age",
            "Experience",
            "Skills",
            "Motivation",
            "Communication",
            "Learning_Attitude",
            "Problem_Solving",
            "Completeness_Score",
            "Quality_Score",
            "Recommendation",
            "Recording_URL"
        ]
        
        body = {
            'values': [headers]
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range='logs!A1:Q1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"✅ logsシートヘッダー設定完了: {result.get('updatedCells', 0)}セル更新")
        
    except Exception as e:
        print(f"❌ logsシートヘッダー設定エラー: {e}")

if __name__ == "__main__":
    initialize_logs_sheet()
