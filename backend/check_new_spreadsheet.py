#!/usr/bin/env python3
"""
Check the structure of the new Google Spreadsheet
"""
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "")
SHEET_ID = os.getenv("SHEET_ID", "")

def check_spreadsheet_structure():
    """新しいスプレッドシートの構造を確認"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        print(f"Checking spreadsheet: {SHEET_ID}")
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        sheets = spreadsheet.get('sheets', [])
        
        print(f"\nAvailable sheets ({len(sheets)} total):")
        for i, sheet in enumerate(sheets):
            sheet_name = sheet['properties']['title']
            sheet_id = sheet['properties']['sheetId']
            print(f"  {i+1}. '{sheet_name}' (ID: {sheet_id})")
            
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=SHEET_ID,
                    range=f"'{sheet_name}'!A1:Z10"
                ).execute()
                values = result.get('values', [])
                print(f"     - Has {len(values)} rows of data")
                if values:
                    print(f"     - Headers: {values[0] if len(values) > 0 else 'No headers'}")
            except Exception as e:
                print(f"     - Error reading sheet: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error accessing spreadsheet: {e}")
        return False

if __name__ == "__main__":
    check_spreadsheet_structure()
