#!/usr/bin/env python3
"""
Diagnose the exact session flow to find why 7-message sessions don't trigger Google Sheets save
"""
import os
import sys
import asyncio
import json
from datetime import datetime

sys.path.append('/home/ubuntu/repos/Radish/backend')

from main import SessionManager, CSVLogger

async def diagnose_session_flow():
    print("=== Diagnosing Session Flow for Google Sheets Save ===")
    
    session_manager = SessionManager()
    csv_logger = CSVLogger()
    
    all_records = csv_logger.get_all_interview_records()
    
    conversations = {}
    for record in all_records:
        conv_id = record.get('conversation_id', 'unknown')
        if conv_id not in conversations:
            conversations[conv_id] = []
        conversations[conv_id].append(record)
    
    print(f"Found {len(conversations)} unique conversations")
    
    for conv_id, messages in conversations.items():
        message_count = len(messages)
        if message_count >= 7:
            print(f"\n=== Analyzing 7+ message conversation: {conv_id} ===")
            print(f"Message count: {message_count}")
            
            session = session_manager.get_session(conv_id)
            if session:
                print(f"✅ Session found in SessionManager")
                print(f"   Session dialogue_count: {session.get('dialogue_count', 'unknown')}")
                print(f"   Session messages count: {len(session.get('messages', []))}")
                print(f"   Session stage: {session.get('stage', 'unknown')}")
                
                if session.get('dialogue_count') != message_count:
                    print(f"⚠️  MISMATCH: Session dialogue_count ({session.get('dialogue_count')}) != CSV message count ({message_count})")
                
                session_messages = session.get('messages', [])
                if len(session_messages) >= 7:
                    print(f"✅ Session has {len(session_messages)} messages for data extraction")
                else:
                    print(f"❌ Session only has {len(session_messages)} messages (needs 7+)")
                    
            else:
                print(f"❌ Session NOT found in SessionManager")
                print(f"   This means the session was not properly maintained in memory")
                print(f"   CSV shows {message_count} messages but SessionManager has no record")
                
                print(f"🔍 ROOT CAUSE CANDIDATE: Session not persisting in SessionManager")
                
    print(f"\n=== SessionManager State ===")
    print(f"Active sessions in memory: {len(session_manager.conversation_sessions)}")
    for session_id, session_data in session_manager.conversation_sessions.items():
        print(f"  Session {session_id}: {session_data.get('dialogue_count', 0)} messages")

if __name__ == "__main__":
    asyncio.run(diagnose_session_flow())
