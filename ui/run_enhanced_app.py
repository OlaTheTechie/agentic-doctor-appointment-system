#!/usr/bin/env python3
"""
Script to run the enhanced Streamlit UI for the Doctor Appointment System
"""

import subprocess
import sys
import os

def main():
    """Run the enhanced Streamlit application"""
    
    # get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "enhanced_app.py")
    
    print("starting enhanced doctor appointment system ui...")
    print(f"app location: {app_path}")
    print("the app will open in your default browser")
    print("url: http://localhost:8501")
    print("\n" + "="*50)
    print("important setup instructions:")
    print("="*50)
    print("1. Make sure the backend API is running:")
    print("   cd backend && python main.py")
    print("   (Should be available at http://127.0.0.1:8000)")
    print("")
    print("2. The UI will show connection status in the header")
    print("3. Use Ctrl+C to stop the Streamlit server")
    print("="*50 + "\n")
    
    try:
        # run streamlit with the enhanced app
        cmd = [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ]
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\nshutting down the enhanced ui...")
    except subprocess.CalledProcessError as e:
        print(f"error running streamlit: {e}")
        print("make sure streamlit is installed: pip install streamlit")
    except Exception as e:
        print(f"unexpected error: {e}")

if __name__ == "__main__":
    main()