#!/usr/bin/env python3
"""
Setup the new spreadsheet with required sheets and data
"""
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "")
OLD_SHEET_ID = "1d5J1znb22828fXIA5Gk6dl4GP7tvqAkaPgQe8zkhi4o"  # Original spreadsheet
NEW_SHEET_ID = "1I0iovuV1lkwIC3lnx7gG92a2MRQu-hLYCdodBplxoNE"  # New spreadsheet

def setup_new_spreadsheet():
    """新しいスプレッドシートに必要なシートとデータを設定"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        print(f"Setting up new spreadsheet: {NEW_SHEET_ID}")
        
        required_sheets = [
            "BasicQuestions",
            "EvaluationCriteria", 
            "NGWords",
            "InterviewFlow",
            "OverallEvaluation",
            "logs"
        ]
        
        new_spreadsheet = service.spreadsheets().get(spreadsheetId=NEW_SHEET_ID).execute()
        existing_sheets = [sheet['properties']['title'] for sheet in new_spreadsheet.get('sheets', [])]
        print(f"Existing sheets: {existing_sheets}")
        
        for sheet_name in required_sheets:
            if sheet_name not in existing_sheets:
                print(f"Creating sheet: {sheet_name}")
                request = {
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }
                service.spreadsheets().batchUpdate(
                    spreadsheetId=NEW_SHEET_ID,
                    body={'requests': [request]}
                ).execute()
        
        for sheet_name in required_sheets[:-1]:  # Skip 'logs' as it should remain empty
            try:
                print(f"Copying data for sheet: {sheet_name}")
                
                result = service.spreadsheets().values().get(
                    spreadsheetId=OLD_SHEET_ID,
                    range=f"{sheet_name}!A:Z"
                ).execute()
                values = result.get('values', [])
                
                if values:
                    body = {'values': values}
                    service.spreadsheets().values().update(
                        spreadsheetId=NEW_SHEET_ID,
                        range=f"{sheet_name}!A1",
                        valueInputOption='USER_ENTERED',
                        body=body
                    ).execute()
                    print(f"  ✅ Copied {len(values)} rows to {sheet_name}")
                else:
                    print(f"  ⚠️ No data found in {sheet_name}")
                    
            except Exception as e:
                print(f"  ❌ Error copying {sheet_name}: {e}")
        
        print("Setting up logs sheet headers...")
        logs_headers = [
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
        
        body = {'values': [logs_headers]}
        service.spreadsheets().values().update(
            spreadsheetId=NEW_SHEET_ID,
            range='logs!A1:Q1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        print("  ✅ Logs sheet headers set")
        
        print(f"\n✅ New spreadsheet setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up new spreadsheet: {e}")
        return False

if __name__ == "__main__":
    setup_new_spreadsheet()
