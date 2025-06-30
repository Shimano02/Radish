#!/usr/bin/env python3
"""
Comprehensive Google Sheets content verification
"""
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def comprehensive_sheets_check():
    print("=== Comprehensive Google Sheets Check ===")
    
    try:
        creds = service_account.Credentials.from_service_account_file(
            'google_service_account.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=creds)
        sheet_id = '1I0iovuV1lkwIC3lnx7gG92a2MRQu-hLYCdodBplxoNE'
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = spreadsheet.get('sheets', [])
        
        print(f"Found {len(sheets)} sheet(s):")
        for sheet in sheets:
            sheet_title = sheet['properties']['title']
            sheet_id_num = sheet['properties']['sheetId']
            print(f"  - '{sheet_title}' (ID: {sheet_id_num})")
        
        for sheet in sheets:
            sheet_title = sheet['properties']['title']
            print(f"\n--- Checking sheet: '{sheet_title}' ---")
            
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"'{sheet_title}'!A:Z"
            ).execute()
            
            values = result.get('values', [])
            print(f"Rows found: {len(values)}")
            
            if values:
                print(f"Headers: {values[0] if values else 'No headers'}")
                for i, row in enumerate(values[1:6], 1):  # Show first 5 data rows
                    print(f"Row {i}: {row}")
                if len(values) > 6:
                    print(f"... and {len(values) - 6} more rows")
            else:
                print("No data found in this sheet")
        
        print(f"\n--- Checking exact range 'A:K' on default sheet ---")
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='A:K'
        ).execute()
        
        values = result.get('values', [])
        print(f"Rows in A:K range: {len(values)}")
        if values:
            for i, row in enumerate(values[:10], 1):
                print(f"Row {i}: {row}")
        
        return True
        
    except Exception as e:
        print(f'Error in comprehensive check: {e}')
        return False

if __name__ == "__main__":
    comprehensive_sheets_check()
