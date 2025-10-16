#!/usr/bin/env python3
"""
enhanced doctor appointment ui - test suite
comprehensive testing for the streamlit ui and backend integration
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# test configuration
API_URL = "http://127.0.0.1:8000/execute"
TEST_PATIENT_ID = 12345678

def check_backend_connection() -> bool:
    """check if the backend api is accessible"""
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        if response.status_code == 200:
            print("backend api is accessible")
            return True
        else:
            print(f"backend api returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"cannot connect to backend api: {e}")
        return False

def test_simple_query():
    """test a simple availability query"""
    print("\ntesting simple availability query...")
    
    payload = {
        "id_number": TEST_PATIENT_ID,
        "messages": [
            {"role": "user", "content": "What doctors are available today?"}
        ],
        "intent": "info_request"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("simple query successful")
            print(f"response messages: {len(data.get('messages', []))}")
            
            # check for repeated routing error
            messages = data.get('messages', [])
            if messages:
                last_message = messages[-1].get('content', '')
                if "Repeated routing detected" in last_message:
                    print("repeated routing detected in response")
                    return False
                else:
                    print("no routing issues detected")
            
            return True
        else:
            print(f"api request failed with status {response.status_code}")
            print(f"response: {response.text}")
            return False
            
    except Exception as e:
        print(f"error during api request: {e}")
        return False

def test_booking_query():
    """test a booking appointment query"""
    print("\ntesting appointment booking query...")
    
    payload = {
        "id_number": TEST_PATIENT_ID,
        "messages": [
            {"role": "user", "content": "I would like to book an appointment for patient ID 12345678 in Dentistry on 2025-10-17 at 10:00"}
        ],
        "intent": "book_appointment"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("booking query successful")
            print(f"response messages: {len(data.get('messages', []))}")
            
            # check for repeated routing error
            messages = data.get('messages', [])
            if messages:
                last_message = messages[-1].get('content', '')
                if "Repeated routing detected" in last_message:
                    print("repeated routing detected in response")
                    return False
                else:
                    print("no routing issues detected")
            
            return True
        else:
            print(f"api request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"error during api request: {e}")
        return False

def test_conversation_flow():
    """test a multi-message conversation to check for routing issues"""
    print("\ntesting conversation flow...")
    
    messages = []
    
    # first message
    payload1 = {
        "id_number": TEST_PATIENT_ID,
        "messages": [
            {"role": "user", "content": "Hello, I need help with appointments"}
        ],
        "intent": "info_request"
    }
    
    try:
        response = requests.post(API_URL, json=payload1, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("first message successful")
            
            # add ai response to conversation
            messages.extend(payload1["messages"])
            if data.get("messages"):
                ai_response = data["messages"][-1]
                messages.append({"role": "ai", "content": ai_response.get("content", "")})
            
            # second message
            messages.append({"role": "user", "content": "What doctors are available today?"})
            
            payload2 = {
                "id_number": TEST_PATIENT_ID,
                "messages": messages,
                "intent": "info_request"
            }
            
            response2 = requests.post(API_URL, json=payload2, timeout=10)
            
            if response2.status_code == 200:
                data2 = response2.json()
                print("second message successful")
                
                # check for repeated routing in either response
                routing_errors = []
                for resp_data in [data, data2]:
                    if resp_data.get("messages"):
                        last_msg = resp_data["messages"][-1].get("content", "")
                        if "Repeated routing detected" in last_msg:
                            routing_errors.append(last_msg)
                
                if routing_errors:
                    print("repeated routing detected in conversation flow")
                    return False
                else:
                    print("conversation flow successful - no routing issues")
                    return True
            else:
                print(f"second message failed with status {response2.status_code}")
                return False
        else:
            print(f"first message failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"error during conversation test: {e}")
        return False

def main():
    """main test function"""
    print("enhanced doctor appointment ui - test suite")
    print("=" * 50)
    print(f"test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"target api: {API_URL}")
    print(f"test patient id: {TEST_PATIENT_ID}")
    print()
    
    # test backend connection first
    if not check_backend_connection():
        print("\nskipping other tests due to api connection failure")
        print("make sure the backend is running: cd backend && python main.py")
        return
    
    # run tests
    tests = [
        ("simple query", test_simple_query()),
        ("booking query", test_booking_query()),
        ("conversation flow", test_conversation_flow())
    ]
    
    # results summary
    print("\n" + "=" * 50)
    print("test summary")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "pass" if result else "fail"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\ntests passed: {passed}/{total}")
    
    if passed == total:
        print("all tests passed! the enhanced ui should work correctly.")
    else:
        print("some tests failed. check the backend and try again.")
        print("see troubleshooting.md for common issues and solutions.")
    
    print(f"\ntest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()