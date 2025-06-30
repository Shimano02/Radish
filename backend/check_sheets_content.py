#!/usr/bin/env python3
"""
Check Google Sheets content directly
"""
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def check_sheets_content():
    print("=== Checking Google Sheets Content ===")
    
    try:
        creds = service_account.Credentials.from_service_account_file(
            'google_service_account.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=creds)
        sheet_id = '1I0iovuV1lkwIC3lnx7gG92a2MRQu-hLYCdodBplxoNE'
        
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='A:Z'
        ).execute()
        
        values = result.get('values', [])
        print(f'Total rows in Google Sheets: {len(values)}')
        
        if values:
            print('Headers:', values[0])
            for i, row in enumerate(values[1:], 1):
                print(f'Row {i}: {row}')
        else:
            print('No data found in spreadsheet')
            
        return len(values)
        
    except Exception as e:
        print(f'Error checking sheets: {e}')
        return 0

if __name__ == "__main__":
    check_sheets_content()
