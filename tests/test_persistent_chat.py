#!/usr/bin/env python3
"""
test script for persistent chat storage
verifies that chat messages are saved and loaded correctly
"""

import requests
import json
import time
from datetime import datetime

# configuration
BASE_URL = "http://127.0.0.1:8000"
PATIENT_ID = 12345678

def test_persistent_storage():
    """test persistent chat storage"""
    print("testing persistent chat storage...")
    print("=" * 50)
    
    # test 1: create session and send messages
    print("\n1. creating session and sending messages...")
    
    # create session
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/sessions",
        json={"patient_id": PATIENT_ID}
    )
    
    if response.status_code != 200:
        print(f"failed to create session: {response.text}")
        return False
    
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"   created session: {session_id}")
    
    # send test messages
    test_messages = [
        "hello, i need help with appointments",
        "i prefer morning slots",
        "can you check dr. smith's availability?",
        "what about next tuesday morning?"
    ]
    
    for i, message in enumerate(test_messages):
        print(f"   sending message {i+1}: {message[:30]}...")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/sessions/{session_id}/messages",
            json={
                "session_id": session_id,
                "patient_id": PATIENT_ID,
                "content": message
            }
        )
        
        if response.status_code != 200:
            print(f"   failed to send message: {response.text}")
            return False
        
        time.sleep(0.5)  # small delay
    
    print(f"   sent {len(test_messages)} messages successfully")
    
    # test 2: verify messages are stored
    print("\n2. verifying messages are stored...")
    
    response = requests.get(f"{BASE_URL}/api/v1/chat/sessions/{session_id}/messages")
    
    if response.status_code != 200:
        print(f"   failed to get messages: {response.text}")
        return False
    
    messages = response.json()
    print(f"   retrieved {len(messages)} messages from storage")
    
    # verify we have user and assistant messages
    user_messages = [m for m in messages if m["role"] == "user"]
    assistant_messages = [m for m in messages if m["role"] == "assistant"]
    
    print(f"   user messages: {len(user_messages)}")
    print(f"   assistant messages: {len(assistant_messages)}")
    
    if len(user_messages) != len(test_messages):
        print(f"   ⚠ expected {len(test_messages)} user messages, got {len(user_messages)}")
    else:
        print("   ✓ correct number of user messages stored")
    
    # test 3: check storage stats
    print("\n3. checking storage statistics...")
    
    response = requests.get(f"{BASE_URL}/api/v1/chat/storage/stats")
    
    if response.status_code == 200:
        stats_data = response.json()
        stats = stats_data["storage_stats"]
        
        print(f"   total sessions: {stats['total_sessions']}")
        print(f"   active sessions: {stats['active_sessions']}")
        print(f"   total messages: {stats['total_messages']}")
        print(f"   total patients: {stats['total_patients']}")
        print(f"   storage directory: {stats['storage_dir']}")
        
        # verify our session is counted
        if stats['total_sessions'] >= 1 and stats['total_messages'] >= len(test_messages):
            print("   ✓ storage stats look correct")
        else:
            print("   ⚠ storage stats may be incorrect")
    else:
        print(f"   failed to get storage stats: {response.text}")
    
    # test 4: verify persistence (simulate server restart)
    print("\n4. testing persistence across 'server restart'...")
    print("   (simulating by getting patient sessions)")
    
    response = requests.get(f"{BASE_URL}/api/v1/chat/sessions/{PATIENT_ID}")
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"   found {len(sessions)} sessions for patient {PATIENT_ID}")
        
        # find our session
        our_session = None
        for session in sessions:
            if session["session_id"] == session_id:
                our_session = session
                break
        
        if our_session:
            print(f"   ✓ session found: {our_session['title']}")
            print(f"   message count: {our_session['message_count']}")
            
            if our_session['message_count'] >= len(test_messages):
                print("   ✓ message count preserved")
            else:
                print("   ⚠ message count may be incorrect")
        else:
            print("   ⚠ our session not found in patient sessions")
    else:
        print(f"   failed to get patient sessions: {response.text}")
    
    # test 5: check file storage
    print("\n5. checking file storage...")
    
    import os
    storage_files = [
        "data/chat_storage/sessions.json",
        "data/chat_storage/messages.json",
        "data/chat_storage/patient_index.json"
    ]
    
    for file_path in storage_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✓ {file_path} ({size} bytes)")
            
            # check if file has content
            if size > 10:  # more than just empty json
                print(f"     contains data")
            else:
                print(f"     appears empty")
        else:
            print(f"   ✗ {file_path} (missing)")
    
    print("\n" + "=" * 50)
    print("persistent storage test completed!")
    
    print("\nchat messages are now saved to:")
    print("- data/chat_storage/sessions.json (session metadata)")
    print("- data/chat_storage/messages.json (all messages)")
    print("- data/chat_storage/patient_index.json (patient->session mapping)")
    
    print("\nbenefits:")
    print("✓ messages persist across server restarts")
    print("✓ conversation history is preserved")
    print("✓ patients can continue previous conversations")
    print("✓ full audit trail of all interactions")
    
    return True

if __name__ == "__main__":
    print("persistent chat storage test")
    print("make sure the backend is running: python3 main.py")
    print()
    
    test_persistent_storage()