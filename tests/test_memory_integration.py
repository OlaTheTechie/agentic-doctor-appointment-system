#!/usr/bin/env python3
"""
test script for memory-powered chat integration
verifies that the memory system works with the enhanced ui
"""

import requests
import json
import time
from datetime import datetime

# configuration
BASE_URL = "http://127.0.0.1:8000"
PATIENT_ID = 12345678

def test_memory_integration():
    """test the complete memory integration"""
    print("testing memory-powered chat integration")
    print("=" * 50)
    
    # test 1: create session
    print("\n1. creating chat session...")
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/sessions",
        json={"patient_id": PATIENT_ID}
    )
    
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"   session created: {session_id}")
    else:
        print(f"   failed to create session: {response.text}")
        return False
    
    # test 2: send messages with memory
    print("\n2. testing memory conversation...")
    
    conversation = [
        "hello, i need to book an appointment",
        "i prefer morning appointments between 9am and 11am",
        "i'd like to see dr. smith if possible",
        "what's dr. smith's availability next week?",
        "actually, what about dr. johnson instead?",
        "can you remind me what time preference i mentioned earlier?"
    ]
    
    for i, message in enumerate(conversation):
        print(f"\n   message {i+1}: {message}")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/sessions/{session_id}/messages",
            json={
                "session_id": session_id,
                "patient_id": PATIENT_ID,
                "content": message
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("ai_response", "")
            context_used = result.get("context_used", False)
            
            print(f"   assistant: {ai_response[:100]}...")
            print(f"   context used: {context_used}")
            
            # the last message should use context to remember preferences
            if i == len(conversation) - 1 and context_used:
                print("   ✓ memory working - context was used!")
            elif i == len(conversation) - 1:
                print("   ⚠ memory may not be working - no context used")
        else:
            print(f"   failed: {response.text}")
            return False
        
        time.sleep(1)  # small delay between messages
    
    # test 3: get session history
    print("\n3. retrieving session history...")
    response = requests.get(f"{BASE_URL}/api/v1/chat/sessions/{session_id}/messages")
    
    if response.status_code == 200:
        messages = response.json()
        print(f"   retrieved {len(messages)} messages")
        
        # verify we have both user and assistant messages
        user_msgs = [m for m in messages if m["role"] == "user"]
        assistant_msgs = [m for m in messages if m["role"] == "assistant"]
        
        print(f"   user messages: {len(user_msgs)}")
        print(f"   assistant messages: {len(assistant_msgs)}")
        
        if len(user_msgs) == len(conversation) and len(assistant_msgs) > 0:
            print("   ✓ message history looks correct")
        else:
            print("   ⚠ message history may be incomplete")
    else:
        print(f"   failed to get history: {response.text}")
    
    # test 4: extract preferences
    print("\n4. testing preference extraction...")
    response = requests.get(f"{BASE_URL}/api/v1/chat/patients/{PATIENT_ID}/preferences")
    
    if response.status_code == 200:
        prefs_data = response.json()
        preferences = prefs_data.get("preferences", {})
        
        print(f"   extracted preferences:")
        for key, value in preferences.items():
            if value:  # only show non-empty preferences
                print(f"     {key}: {value}")
        
        # check if morning preference was detected
        if "morning" in str(preferences).lower():
            print("   ✓ morning preference detected!")
        else:
            print("   ⚠ morning preference not detected")
    else:
        print(f"   failed to get preferences: {response.text}")
    
    # test 5: search conversations
    print("\n5. testing conversation search...")
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/patients/{PATIENT_ID}/search",
        params={"query": "morning"}
    )
    
    if response.status_code == 200:
        search_results = response.json()
        matches = search_results.get("total_matches", 0)
        
        print(f"   found {matches} matches for 'morning'")
        
        if matches > 0:
            print("   ✓ search functionality working")
            # show first result
            if search_results.get("results"):
                first_result = search_results["results"][0]
                print(f"   first match: {first_result['content'][:80]}...")
        else:
            print("   ⚠ no search results found")
    else:
        print(f"   failed to search: {response.text}")
    
    print("\n" + "=" * 50)
    print("memory integration test completed!")
    print("\nto test the ui integration:")
    print("1. start the backend: python3 main.py")
    print("2. start the ui: python3 ui/run_enhanced_app.py")
    print("3. enable 'memory chat' in the sidebar")
    print("4. start a conversation and see context being used")
    
    return True

def test_ui_endpoints():
    """test endpoints that the ui will use"""
    print("\ntesting ui-specific endpoints...")
    
    # test health check
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ health endpoint working")
        else:
            print("⚠ health endpoint issues")
    except:
        print("✗ health endpoint not accessible")
    
    # test original execute endpoint
    try:
        response = requests.post(
            f"{BASE_URL}/execute",
            json={
                "id_number": PATIENT_ID,
                "messages": [{"role": "user", "content": "test message"}],
                "intent": "info_request"
            },
            timeout=10
        )
        if response.status_code == 200:
            print("✓ original execute endpoint working")
        else:
            print("⚠ original execute endpoint issues")
    except:
        print("✗ original execute endpoint not accessible")

if __name__ == "__main__":
    print("memory-powered chat integration test")
    print("make sure the backend is running: python3 main.py")
    print()
    
    # test ui endpoints first
    test_ui_endpoints()
    
    # test memory integration
    test_memory_integration()