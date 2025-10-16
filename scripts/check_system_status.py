#!/usr/bin/env python3
"""
Quick system status check for the Doctor Appointment System
"""

import requests
import subprocess
import sys

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print("Backend: RUNNING")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Agent: {'OK' if data.get('agent_initialized') else 'ERROR'}")
            print(f"   Data: {'OK' if data.get('data_file_available') else 'ERROR'}")
            return True
    except Exception as e:
        print(f"Backend: NOT RUNNING ({e})")
    return False

def check_streamlit():
    """Check if Streamlit UI is running"""
    try:
        response = requests.get("http://127.0.0.1:8502", timeout=3)
        if response.status_code == 200:
            print("Streamlit UI: RUNNING on http://localhost:8502")
            return True
    except:
        pass
    
    try:
        response = requests.get("http://127.0.0.1:8501", timeout=3)
        if response.status_code == 200:
            print("Streamlit UI: RUNNING on http://localhost:8501")
            return True
    except:
        pass
    
    print("Streamlit UI: NOT RUNNING")
    return False

def test_api_connection():
    """Test API connection"""
    try:
        payload = {
            "id_number": 12345678,
            "messages": [{"role": "user", "content": "system status check"}],
            "intent": "info_request"
        }
        
        response = requests.post("http://127.0.0.1:8000/execute", json=payload, timeout=15)
        if response.status_code == 200:
            print("API Connection: WORKING")
            return True
        else:
            print(f"API Connection: ERROR ({response.status_code})")
    except Exception as e:
        print(f"API Connection: FAILED ({e})")
    return False

def main():
    """Main status check"""
    print("Doctor Appointment System - Status Check")
    print("=" * 50)
    
    backend_ok = check_backend()
    streamlit_ok = check_streamlit()
    api_ok = test_api_connection() if backend_ok else False
    
    print("\n" + "=" * 50)
    print("System Status Summary:")
    
    if backend_ok and streamlit_ok and api_ok:
        print("ALL SYSTEMS OPERATIONAL!")
        print("\nAccess Points:")
        print("   • Streamlit UI: http://localhost:8502 (or 8501)")
        print("   • Backend API: http://127.0.0.1:8000")
        print("   • API Docs: http://127.0.0.1:8000/docs (if available)")
        print("\n✨ Your enhanced appointment system is ready to use!")
        
    elif backend_ok and api_ok:
        print("Backend working, but Streamlit UI needs to be started")
        print("\nTo start Streamlit UI:")
        print("   cd backend/ui && source ../.venv/bin/activate && streamlit run enhanced_app.py")
        
    elif backend_ok:
        print("Backend running but API has issues")
        print("Check backend logs for errors")
        
    else:
        print("System not operational")
        print("\nTo start the system:")
        print("1. Start Backend:")
        print("   cd backend && source .venv/bin/activate && python start_server.py")
        print("2. Start UI (in new terminal):")
        print("   cd backend/ui && source ../.venv/bin/activate && streamlit run enhanced_app.py")

if __name__ == "__main__":
    main()