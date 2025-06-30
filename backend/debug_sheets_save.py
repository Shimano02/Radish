#!/usr/bin/env python3
"""
Debug script to investigate why 7-message sessions aren't saving to Google Sheets
"""
import os
import sys
import asyncio
import json
from datetime import datetime

sys.path.append('/home/ubuntu/repos/Radish/backend')

from main import GoogleSheetsService, StructuredDataExtractor, SessionManager, CSVLogger

async def debug_sheets_save_issue():
    print("=== Debugging Google Sheets Save Issue ===")
    
    print(f"GOOGLE_SERVICE_ACCOUNT_PATH exists: {os.path.exists('google_service_account.json')}")
    print(f"SHEET_ID configured: {'1I0iovuV1lkwIC3lnx7gG92a2MRQu-hLYCdodBplxoNE' is not None}")
    
    csv_logger = CSVLogger()
    all_records = csv_logger.get_all_interview_records()
    
    print(f"\nTotal CSV records found: {len(all_records)}")
    
    conversations = {}
    for record in all_records:
        conv_id = record.get('conversation_id', 'unknown')
        if conv_id not in conversations:
            conversations[conv_id] = []
        conversations[conv_id].append(record)
    
    print(f"Unique conversations: {len(conversations)}")
    
    for conv_id, messages in conversations.items():
        message_count = len(messages)
        print(f"\nConversation {conv_id}: {message_count} messages")
        
        if message_count >= 7:
            print(f"  ✅ Should trigger Google Sheets save (7+ messages)")
            
            conversation_text = ""
            for msg in messages:
                role = "面接官" if msg.get('interviewer_id') == 'fudou' else "応募者"
                content = msg.get('ai_response', '') if role == "面接官" else msg.get('user_message', '')
                if content:
                    conversation_text += f"{role}: {content}\n"
            
            print(f"  Conversation text length: {len(conversation_text)} characters")
            
            try:
                from main import OpenAIAPIClient
                openai_client = OpenAIAPIClient(os.getenv("OPENAI_API_KEY"))
                extracted_data = await StructuredDataExtractor.extract_interview_data(
                    messages, openai_client
                )
                print(f"  Data extraction result: {extracted_data}")
                
                if extracted_data:
                    save_result = await GoogleSheetsService.save_interview_data(
                        conv_id, extracted_data
                    )
                    print(f"  Google Sheets save result: {save_result}")
                else:
                    print(f"  ❌ No data extracted")
                    
            except Exception as e:
                print(f"  ❌ Error during extraction/save: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  ⏸️  Below threshold (needs 7+ messages)")

if __name__ == "__main__":
    asyncio.run(debug_sheets_save_issue())
