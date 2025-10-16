import streamlit as st
import requests
import json
from datetime import datetime, date, time
from typing import Dict, List, Any, Optional
import time as time_module

# page configuration
st.set_page_config(
    page_title="Doctor Appointment System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# api configuration
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# API configuration with environment-based URL
import os

# Get backend URL from environment or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
API_URL = f"{BACKEND_URL}/execute"
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))

# For Streamlit Cloud deployment, check if secrets are available
# BUT prioritize local development (only use secrets if not running locally)
try:
    if hasattr(st, 'secrets') and 'api' in st.secrets:
        # Only use secrets if we're not running on localhost
        secrets_url = st.secrets["api"]["backend_url"]
        if "localhost" not in secrets_url and "127.0.0.1" not in secrets_url:
            # We're in production, use secrets
            BACKEND_URL = secrets_url
            API_URL = f"{BACKEND_URL}/execute"
            REQUEST_TIMEOUT = st.secrets["api"]["request_timeout"]
        # If secrets contain localhost, we're in local dev, keep defaults
except Exception:
    pass  # Use environment variables or defaults

# custom css for professional medical theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #16a34a;
        box-shadow: 0 0 8px #16a34a;
    }
    
    .status-offline {
        background-color: #ef4444;
        box-shadow: 0 0 8px #ef4444;
    }
    
    .chat-container {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .user-message {
        background-color: #2563eb;
        color: white;
        padding: 0.8rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .system-message {
        background-color: #e5e7eb;
        color: #1f2937;
        padding: 0.8rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        line-height: 1.5;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .timestamp {
        font-size: 0.7rem;
        color: #6b7280;
        margin-top: 0.3rem;
    }
    
    .form-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .success-message {
        background-color: #dcfce7;
        border-left: 4px solid #16a34a;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-message {
        background-color: #fef3c7;
        border-left: 4px solid #ea580c;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Improved table styling for chat messages */
    .system-message table {
        border-collapse: collapse;
        margin: 10px 0;
        width: 100%;
        font-size: 0.9rem;
    }
    
    .system-message th {
        border: 1px solid #ddd;
        padding: 8px;
        background-color: #f2f2f2;
        font-weight: bold;
        text-align: left;
    }
    
    .system-message td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    /* Better formatting for lists in chat */
    .system-message ul {
        margin: 10px 0;
        padding-left: 20px;
    }
    
    .system-message li {
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """initialize all session state variables including memory chat"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Book Appointment"
    if "api_status" not in st.session_state:
        st.session_state.api_status = False
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    if "last_response" not in st.session_state:
        st.session_state.last_response = {}
    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = {
            "next": "",
            "current_reasoning": "",
            "step_count": 0
        }
    # memory chat session state
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []
    if "memory_enabled" not in st.session_state:
        st.session_state.memory_enabled = True
    if "patient_preferences" not in st.session_state:
        st.session_state.patient_preferences = {}

def check_api_status() -> bool:
    """check if the backend api is accessible"""
    try:
        # Use the configured backend URL instead of hardcoded localhost
        health_url = f"{BACKEND_URL}/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            return True
        
        # fallback to docs endpoint
        docs_url = f"{BACKEND_URL}/docs"
        response = requests.get(docs_url, timeout=5)
        return response.status_code == 200
    except:
        return False

# memory chat functions
def create_chat_session(patient_id: int) -> str:
    """create a new memory-powered chat session"""
    try:
        url = f"{API_URL.replace('/execute', '')}/api/v1/chat/sessions"
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"patient_id": patient_id},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            session_data = response.json()
            return session_data["session_id"]
        else:
            st.error(f"failed to create chat session: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"error creating chat session: {str(e)}")
        return None

def get_patient_sessions(patient_id: int) -> List[Dict]:
    """get all chat sessions for a patient"""
    try:
        response = requests.get(
            f"{API_URL.replace('/execute', '')}/api/v1/chat/sessions/{patient_id}",
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"error fetching sessions: {str(e)}")
        return []

def send_memory_message(session_id: str, patient_id: int, message: str) -> Dict:
    """send message using memory-powered chat"""
    try:
        response = requests.post(
            f"{API_URL.replace('/execute', '')}/api/v1/chat/sessions/{session_id}/messages",
            json={
                "session_id": session_id,
                "patient_id": patient_id,
                "content": message
            },
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"api error: {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"request failed: {str(e)}"}

def get_session_messages(session_id: str) -> List[Dict]:
    """get messages from a chat session"""
    try:
        response = requests.get(
            f"{API_URL.replace('/execute', '')}/api/v1/chat/sessions/{session_id}/messages",
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"error fetching messages: {str(e)}")
        return []

def get_patient_preferences(patient_id: int) -> Dict:
    """get extracted preferences from chat history"""
    try:
        response = requests.get(
            f"{API_URL.replace('/execute', '')}/api/v1/chat/patients/{patient_id}/preferences",
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"preferences": {}}
    except Exception as e:
        return {"preferences": {}}

def add_message(role: str, content: str):
    """add a message to the conversation history"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

def clean_text_content(content: str) -> str:
    """clean text content for display - remove all formatting"""
    if not content:
        return content
    
    import re
    
    # remove all markdown formatting
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Remove bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)      # Remove italic
    content = re.sub(r'`(.*?)`', r'\1', content)        # Remove code
    content = re.sub(r'#{1,6}\s*', '', content)         # Remove headers
    
    # clean up bullet points
    content = re.sub(r'^[\s]*[-\*\+]\s*', '• ', content, flags=re.MULTILINE)
    
    # remove extra whitespace but preserve line breaks
    lines = [line.strip() for line in content.split('\n')]
    content = '\n'.join(line for line in lines if line)
    
    return content

def extract_ai_response(response_data: dict) -> str:
    """extract the ai response from the api response data"""
    if not response_data.get("messages"):
        return "No response received"
    
    # get the latest ai response from the backend
    # look for ai messages first, then fall back to any non-user message
    ai_messages = [msg for msg in response_data["messages"] if msg.get("role") in ["ai", "assistant"]]
    
    if ai_messages:
        return ai_messages[-1]["content"]
    else:
        # fallback: get the last message that's not from the user
        all_messages = response_data["messages"]
        non_user_messages = [msg for msg in all_messages if msg.get("role") not in ["user", "human"] or 
                           (msg.get("content", "").startswith("I") and len(msg.get("content", "")) > 50)]
        
        if non_user_messages:
            return non_user_messages[-1]["content"]
        else:
            # last resort: get the last message
            return all_messages[-1]["content"] if all_messages else "No response received"

def display_memory_chat_interface():
    """display enhanced chat interface with memory sessions"""
    st.markdown("### Memory-Powered Chat")
    
    # session management header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.session_state.current_session_id:
            st.markdown(f"**Active Session:** `{st.session_state.current_session_id[:12]}...`")
        else:
            st.markdown("**No active session** - Create or select one below")
    
    with col2:
        if st.button("New Session", key="new_session", use_container_width=True):
            # get patient id from user input or default
            patient_id = st.session_state.user_data.get("patient_id", 12345678)
            session_id = create_chat_session(patient_id)
            if session_id:
                st.session_state.current_session_id = session_id
                st.session_state.messages = []  # clear current messages
                st.success(f"New session created!")
                st.rerun()
    
    with col3:
        if st.button("Load Sessions", key="load_sessions", use_container_width=True):
            patient_id = st.session_state.user_data.get("patient_id", 12345678)
            sessions = get_patient_sessions(patient_id)
            st.session_state.chat_sessions = sessions
            if sessions:
                st.success(f"Loaded {len(sessions)} sessions")
            else:
                st.info("No previous sessions found")
    
    # session selector
    if st.session_state.chat_sessions:
        st.markdown("**Previous Sessions:**")
        session_options = {}
        for session in st.session_state.chat_sessions:
            title = session.get("title", "Untitled")
            created = session.get("created_at", "")[:10]  # date only
            msg_count = session.get("message_count", 0)
            display_name = f"{title} ({created}) - {msg_count} messages"
            session_options[display_name] = session["session_id"]
        
        if session_options:
            selected_session = st.selectbox(
                "Select a session to continue:",
                options=list(session_options.keys()),
                key="session_selector"
            )
            
            if selected_session and st.button("Load Selected Session", key="load_selected"):
                session_id = session_options[selected_session]
                st.session_state.current_session_id = session_id
                
                # load session messages
                messages = get_session_messages(session_id)
                st.session_state.messages = []
                
                for msg in messages:
                    st.session_state.messages.append({
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": msg["timestamp"][:8]  # time only
                    })
                
                st.success(f"Loaded session with {len(messages)} messages")
                st.rerun()
    
    # enhanced chat container with memory indicators
    chat_html = '<div class="chat-container">'
    
    # memory status indicator
    if st.session_state.current_session_id and st.session_state.memory_enabled:
        chat_html += '''
        <div style="background: #e0f2fe; border-left: 4px solid #0288d1; padding: 0.5rem; margin-bottom: 1rem; border-radius: 4px;">
            <small style="color: #0277bd;"><strong>Memory Active:</strong> This conversation remembers context from previous messages</small>
        </div>
        '''
    
    if not st.session_state.messages:
        welcome_text = "Welcome to the Memory-Powered Doctor Appointment System!" if st.session_state.memory_enabled else "Welcome to the Doctor Appointment System!"
        chat_html += f'''
        <div style="text-align: center; padding: 2rem; color: #6b7280;">
            <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">{welcome_text}</p>
            <p style="font-style: italic;">Start a conversation or use the forms above to book appointments and check availability.</p>
            {f'<p style="font-size: 0.9rem; color: #0288d1;">Session: {st.session_state.current_session_id[:12]}...</p>' if st.session_state.current_session_id else ''}
        </div>
        '''
    else:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                chat_html += f'''
                <div class="user-message">
                    <strong>You:</strong><br>
                    {msg["content"]}
                    <div class="timestamp">{msg.get("timestamp", "")}</div>
                </div>
                '''
            elif msg["role"] in ["assistant", "system"]:
                # clean the content to remove all formatting
                content = clean_text_content(msg["content"])
                
                # replace newlines with html breaks for display
                content = content.replace('\n', '<br>')
                
                # add memory context indicator for assistant messages
                memory_indicator = ""
                if st.session_state.memory_enabled and i > 0:
                    memory_indicator = '<small style="color: #0288d1; font-style: italic;">● Context-aware response</small><br>'
                
                chat_html += f'''
                <div class="system-message">
                    <strong>Assistant:</strong><br>
                    {memory_indicator}
                    {content}
                    <div class="timestamp">{msg.get("timestamp", "")}</div>
                </div>
                '''
    
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
    
    # direct chat input section
    st.markdown("---")
    st.markdown("**Quick Chat:**")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        chat_input = st.text_input(
            "Type your message here...",
            key="direct_chat_input",
            placeholder="Ask about appointments, availability, or any questions..."
        )
    
    with col2:
        send_chat = st.button("Send", key="send_chat", use_container_width=True)
    
    if send_chat and chat_input.strip():
        # ensure we have a session
        if not st.session_state.current_session_id:
            patient_id = st.session_state.user_data.get("patient_id", 12345678)
            session_id = create_chat_session(patient_id)
            if session_id:
                st.session_state.current_session_id = session_id
            else:
                st.error("Failed to create chat session")
                return
        
        # send message with memory
        patient_id = st.session_state.user_data.get("patient_id", 12345678)
        
        if st.session_state.memory_enabled and st.session_state.current_session_id:
            # use memory-powered chat
            result = send_memory_message(st.session_state.current_session_id, patient_id, chat_input)
            
            if result["success"]:
                # add messages to display
                add_message("user", chat_input)
                
                response_data = result["data"]
                ai_response = response_data.get("ai_response", "No response received")
                add_message("assistant", ai_response)
                
                # show memory context indicator
                if response_data.get("context_used"):
                    st.success("Response generated using conversation context")
                
                st.rerun()
            else:
                st.error(f"Chat failed: {result['error']}")
        else:
            # fallback to regular api
            result = send_api_request(chat_input, patient_id, "info_request")
            
            if result["success"]:
                add_message("user", chat_input)
                
                response_data = result["data"]
                system_response = extract_ai_response(response_data)
                add_message("assistant", system_response)
                
                st.rerun()
            else:
                st.error(f"Chat failed: {result['error']}")
    
    # auto-scroll to bottom (javascript)
    st.markdown("""
    <script>
        var chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
    """, unsafe_allow_html=True)

def validate_patient_id(patient_id: str) -> bool:
    """validate patient id format (7-8 digits)"""
    return patient_id.isdigit() and 7 <= len(patient_id) <= 8

def send_api_request(query: str, patient_id: int, intent: str = "info_request") -> Dict[str, Any]:
    """send request to the backend api with optional memory integration"""
    try:
        # check if memory is enabled and we have an active session
        if st.session_state.memory_enabled and st.session_state.current_session_id:
            # use memory-powered chat
            result = send_memory_message(st.session_state.current_session_id, patient_id, query)
            if result["success"]:
                # convert memory response to standard format
                memory_data = result["data"]
                return {
                    "success": True,
                    "data": {
                        "messages": [{"role": "assistant", "content": memory_data.get("ai_response", "")}],
                        "agent_used": memory_data.get("agent_used", "memory_agent"),
                        "context_used": memory_data.get("context_used", False),
                        "is_complete": memory_data.get("is_complete", True)
                    }
                }
            # if memory fails, fall back to regular api
        
        # regular api request (fallback or when memory disabled)
        api_messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                api_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] in ["system", "assistant"]:
                api_messages.append({"role": "ai", "content": msg["content"]})
        
        # only add current query if it's not already in the messages
        if not api_messages or api_messages[-1]["content"] != query:
            api_messages.append({"role": "user", "content": query})
        
        payload = {
            "id_number": patient_id,
            "messages": api_messages,
            "intent": intent,
            "query": query,
            "next": st.session_state.conversation_state.get("next", ""),
            "current_reasoning": st.session_state.conversation_state.get("current_reasoning", ""),
            "step_count": st.session_state.conversation_state.get("step_count", 0)
        }
        
        with st.spinner("Processing your request..."):
            response = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # update conversation state from backend response
            st.session_state.conversation_state = {
                "next": response_data.get("next", ""),
                "current_reasoning": response_data.get("current_reasoning", ""),
                "step_count": response_data.get("step_count", 0)
            }
            
            return {"success": True, "data": response_data}
        else:
            return {"success": False, "error": f"API Error {response.status_code}: {response.text}"}
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to the backend service."}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def display_header():
    """display the main header with status and branding"""
    st.session_state.api_status = check_api_status()
    
    status_class = "status-online" if st.session_state.api_status else "status-offline"
    status_text = "Connected" if st.session_state.api_status else "Disconnected"
    
    header_html = f'''
    <div class="main-header">
        <h1>Doctor Appointment Multi-Agent System</h1>
        <p>
            <span class="status-indicator {status_class}"></span>
            Backend Status: {status_text} • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </p>
    </div>
    '''
    
    st.markdown(header_html, unsafe_allow_html=True)

def book_appointment_panel():
    """panel for booking new appointments"""
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### Book New Appointment")
    
    with st.form("book_appointment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input(
                "Patient ID *", 
                placeholder="Enter 7-8 digit ID",
                help="Your unique patient identification number"
            )
            doctor_name = st.text_input(
                "Doctor Name", 
                placeholder="e.g., Dr. Smith",
                help="Preferred doctor (optional)"
            )
            specialization = st.selectbox(
                "Specialization *",
                ["", "General Practice", "Cardiology", "Dermatology", "Dentistry", 
                 "Orthopedics", "Pediatrics", "Psychiatry", "Neurology", "Other"],
                help="Medical specialization required"
            )
        
        with col2:
            appointment_date = st.date_input(
                "Preferred Date *",
                min_value=date.today(),
                help="Select your preferred appointment date"
            )
            appointment_time = st.time_input(
                "Preferred Time *",
                value=time(9, 0),
                help="Select your preferred appointment time"
            )
            notes = st.text_area(
                "Additional Notes",
                placeholder="Any specific requirements or symptoms...",
                help="Optional additional information"
            )
        
        submitted = st.form_submit_button("Book Appointment", use_container_width=True)
        
        if submitted:
            # Validation
            if not patient_id or not validate_patient_id(patient_id):
                st.error("Please enter a valid Patient ID (7-8 digits)")
            elif not specialization:
                st.error("Please select a specialization")
            else:
                # Construct query
                query_parts = [f"I would like to book an appointment for patient ID {patient_id}"]
                if doctor_name:
                    query_parts.append(f"with Dr. {doctor_name}")
                query_parts.append(f"in {specialization}")
                query_parts.append(f"on {appointment_date.strftime('%Y-%m-%d')} at {appointment_time.strftime('%H:%M')}")
                if notes:
                    query_parts.append(f"Additional notes: {notes}")
                
                query = " ".join(query_parts)
                
                # Send API request first
                result = send_api_request(query, int(patient_id), "book_appointment")
                
                if result["success"]:
                    # Add user message to conversation history
                    add_message("user", query)
                    
                    response_data = result["data"]
                    system_response = extract_ai_response(response_data)
                    
                    # Check for repeated routing error
                    if "Repeated routing detected" in system_response:
                        add_message("system", "I noticed we're going in circles. Let me reset and try a fresh approach. Please rephrase your request or try again.")
                        st.warning("Conversation loop detected. Please try rephrasing your request.")
                        # reset conversation state
                        st.session_state.conversation_state = {"next": "", "current_reasoning": "", "step_count": 0}
                    elif system_response and len(system_response.strip()) > 10:
                        add_message("system", system_response)
                        st.success("Appointment request processed successfully!")
                    else:
                        add_message("system", "Request processed, but no clear response received. Please try rephrasing your request.")
                        st.warning("Request processed but response was unclear.")
                    st.rerun()
                else:
                    st.error(f"{result['error']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def check_availability_panel():
    """panel for checking doctor availability"""
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### Check Availability")
    
    with st.form("check_availability_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input(
                "Patient ID", 
                placeholder="Enter 7-8 digit ID (optional)",
                help="Your patient ID for personalized results"
            )
            doctor_name = st.text_input(
                "Doctor Name", 
                placeholder="e.g., Dr. Smith (optional)",
                help="Specific doctor to check availability for"
            )
            specialization = st.selectbox(
                "Specialization",
                ["", "General Practice", "Cardiology", "Dermatology", "Dentistry", 
                 "Orthopedics", "Pediatrics", "Psychiatry", "Neurology", "Other"],
                help="Medical specialization to check"
            )
        
        with col2:
            start_date = st.date_input(
                "From Date",
                value=date.today(),
                min_value=date.today(),
                help="Start date for availability check"
            )
            end_date = st.date_input(
                "To Date",
                value=date.today(),
                min_value=date.today(),
                help="End date for availability check"
            )
            time_preference = st.selectbox(
                "Time Preference",
                ["Any time", "Morning (9AM-12PM)", "Afternoon (12PM-5PM)", "Evening (5PM-8PM)"],
                help="Preferred time slot"
            )
        
        submitted = st.form_submit_button("Check Availability", use_container_width=True)
        
        if submitted:
            # Construct query
            query_parts = ["I would like to check availability"]
            if doctor_name:
                query_parts.append(f"for Dr. {doctor_name}")
            if specialization:
                query_parts.append(f"in {specialization}")
            
            if start_date == end_date:
                query_parts.append(f"on {start_date.strftime('%Y-%m-%d')}")
            else:
                query_parts.append(f"from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            if time_preference != "Any time":
                query_parts.append(f"during {time_preference.lower()}")
            
            query = " ".join(query_parts)
            
            # Send API request first
            pid = int(patient_id) if patient_id and validate_patient_id(patient_id) else 12345678
            result = send_api_request(query, pid, "info_request")
            
            if result["success"]:
                # Add user message to conversation history
                add_message("user", query)
                
                response_data = result["data"]
                system_response = extract_ai_response(response_data)
                
                # check for repeated routing error
                if "Repeated routing detected" in system_response:
                    add_message("system", "I noticed we're going in circles. Let me reset and try a fresh approach. Please rephrase your request or try again.")
                    st.warning("Conversation loop detected. Please try rephrasing your request.")
                    # reset conversation state
                    st.session_state.conversation_state = {"next": "", "current_reasoning": "", "step_count": 0}
                elif system_response and len(system_response.strip()) > 10:
                    add_message("system", system_response)
                    st.success("Availability check completed!")
                else:
                    add_message("system", "Availability check processed, but no clear response received. Please try rephrasing your request.")
                    st.warning("Check processed but response was unclear.")
                st.rerun()
            else:
                st.error(f"{result['error']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def cancel_reschedule_panel():
    """Panel for canceling or rescheduling appointments"""
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### Cancel or Reschedule Appointment")
    
    with st.form("cancel_reschedule_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input(
                "Patient ID *", 
                placeholder="Enter 7-8 digit ID",
                help="Your unique patient identification number"
            )
            action_type = st.radio(
                "Action *",
                ["Cancel Appointment", "Reschedule Appointment"],
                help="Choose whether to cancel or reschedule"
            )
            current_date = st.date_input(
                "Current Appointment Date *",
                help="Date of the appointment to cancel/reschedule"
            )
            current_time = st.time_input(
                "Current Appointment Time",
                help="Time of the appointment (if known)"
            )
        
        with col2:
            doctor_name = st.text_input(
                "Doctor Name",
                placeholder="e.g., Dr. Smith",
                help="Doctor for the current appointment"
            )
            
            if action_type == "Reschedule Appointment":
                st.markdown("**New Appointment Details:**")
                new_date = st.date_input(
                    "New Date *",
                    min_value=date.today(),
                    help="New preferred date"
                )
                new_time = st.time_input(
                    "New Time *",
                    value=time(9, 0),
                    help="New preferred time"
                )
            
            reason = st.text_area(
                "Reason (Optional)",
                placeholder="Reason for cancellation/rescheduling...",
                help="Optional reason for the change"
            )
        
        submitted = st.form_submit_button(f"{action_type}", use_container_width=True)
        
        if submitted:
            # Validation
            if not patient_id or not validate_patient_id(patient_id):
                st.error("Please enter a valid Patient ID (7-8 digits)")
            else:
                # Construct query
                if action_type == "Cancel Appointment":
                    query_parts = [f"I would like to cancel my appointment for patient ID {patient_id}"]
                    query_parts.append(f"on {current_date.strftime('%Y-%m-%d')}")
                    if current_time:
                        query_parts.append(f"at {current_time.strftime('%H:%M')}")
                    if doctor_name:
                        query_parts.append(f"with Dr. {doctor_name}")
                    intent = "cancel_appointment"
                else:
                    query_parts = [f"I would like to reschedule my appointment for patient ID {patient_id}"]
                    query_parts.append(f"from {current_date.strftime('%Y-%m-%d')}")
                    if current_time:
                        query_parts.append(f"at {current_time.strftime('%H:%M')}")
                    if doctor_name:
                        query_parts.append(f"with Dr. {doctor_name}")
                    query_parts.append(f"to {new_date.strftime('%Y-%m-%d')} at {new_time.strftime('%H:%M')}")
                    intent = "reschedule_appointment"
                
                if reason:
                    query_parts.append(f"Reason: {reason}")
                
                query = " ".join(query_parts)
                
                # Send API request first
                result = send_api_request(query, int(patient_id), intent)
                
                if result["success"]:
                    # Add user message to conversation history
                    add_message("user", query)
                    
                    response_data = result["data"]
                    system_response = extract_ai_response(response_data)
                    
                    # Check for repeated routing error
                    if "Repeated routing detected" in system_response:
                        add_message("system", "I noticed we're going in circles. Let me reset and try a fresh approach. Please rephrase your request or try again.")
                        st.warning("Conversation loop detected. Please try rephrasing your request.")
                        # Reset conversation state
                        st.session_state.conversation_state = {"next": "", "current_reasoning": "", "step_count": 0}
                    elif system_response and len(system_response.strip()) > 10:
                        add_message("system", system_response)
                        st.success(f"{action_type} request processed successfully!")
                    else:
                        add_message("system", f"{action_type} processed, but no clear response received. Please try rephrasing your request.")
                        st.warning("Request processed but response was unclear.")
                    st.rerun()
                else:
                    st.error(f"{result['error']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def general_query_panel():
    """Panel for general queries and questions"""
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### General Query")
    
    # Quick action buttons
    st.markdown("**Quick Actions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("My Appointments", use_container_width=True):
            st.session_state.quick_query = "Show me all my upcoming appointments"
    
    with col2:
        if st.button("Available Doctors", use_container_width=True):
            st.session_state.quick_query = "What doctors are available today?"
    
    with col3:
        if st.button("Help", use_container_width=True):
            st.session_state.quick_query = "How can I book an appointment?"
    
    with st.form("general_query_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            query_text = st.text_area(
                "Your Question *",
                value=st.session_state.get("quick_query", ""),
                placeholder="Ask anything about appointments, doctors, or the system...",
                help="Type your question or use the quick action buttons above",
                height=100
            )
        
        with col2:
            patient_id = st.text_input(
                "Patient ID (Optional)", 
                placeholder="Enter 7-8 digit ID",
                help="Include for personalized responses"
            )
            
            st.markdown("**Example queries:**")
            st.markdown("- What specialists are available?")
            st.markdown("- Show my appointment history")
            st.markdown("- How do I cancel an appointment?")
            st.markdown("- What are the clinic hours?")
        
        submitted = st.form_submit_button("Send Query", use_container_width=True)
        
        if submitted:
            if not query_text.strip():
                st.error("Please enter a question or query")
            else:
                # Send API request first
                pid = int(patient_id) if patient_id and validate_patient_id(patient_id) else 12345678
                result = send_api_request(query_text, pid, "info_request")
                
                if result["success"]:
                    # Add user message to conversation history
                    add_message("user", query_text)
                    
                    response_data = result["data"]
                    if response_data.get("messages"):
                        system_response = extract_ai_response(response_data)
                        
                        # check for repeated routing error
                        if "Repeated routing detected" in system_response:
                            add_message("system", "I noticed we're going in circles. Let me reset and try a fresh approach. Please rephrase your request or try again.")
                            st.warning("Conversation loop detected. Please try rephrasing your request.")
                            # reset conversation state
                            st.session_state.conversation_state = {"next": "", "current_reasoning": "", "step_count": 0}
                        elif system_response and len(system_response.strip()) > 10:
                            add_message("system", system_response)
                            st.success("Query processed successfully!")
                        else:
                            add_message("system", "Query processed, but no clear response received. Please try rephrasing your question.")
                            st.warning("Query processed but response was unclear.")
                    st.rerun()
                else:
                    st.error(f"{result['error']}")
    
    # clear quick query after form submission
    if "quick_query" in st.session_state:
        del st.session_state.quick_query
    
    st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# Display header
display_header()

# Main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Navigation")
    
    # tab selection
    tabs = [
        ("Book Appointment", "Book Appointment"),
        ("Check Availability", "Check Availability"), 
        ("Cancel/Reschedule", "Cancel/Reschedule"),
        ("General Query", "General Query")
    ]
    
    for tab_display, tab_key in tabs:
        # highlight current tab with different styling
        if st.session_state.current_tab == tab_key:
            st.success(f"Current: {tab_display}")
        else:
            if st.button(tab_display, key=f"tab_{tab_key}", use_container_width=True):
                st.session_state.current_tab = tab_key
                st.rerun()
    
    st.markdown("---")
    
    # memory controls
    st.markdown("### Memory & Sessions")
    
    # memory toggle
    memory_enabled = st.checkbox(
        "Enable Memory Chat",
        value=st.session_state.memory_enabled,
        help="Remember conversation context across messages"
    )
    
    if memory_enabled != st.session_state.memory_enabled:
        st.session_state.memory_enabled = memory_enabled
        st.rerun()
    
    # session info
    if st.session_state.current_session_id:
        st.success(f"Active Session")
        st.caption(f"ID: {st.session_state.current_session_id[:12]}...")
        
        # load preferences button
        if st.button("Load My Preferences", use_container_width=True):
            patient_id = st.session_state.user_data.get("patient_id", 12345678)
            prefs = get_patient_preferences(patient_id)
            st.session_state.patient_preferences = prefs.get("preferences", {})
            if st.session_state.patient_preferences:
                st.success("Preferences loaded!")
            else:
                st.info("No preferences found yet")
    else:
        st.info("No active session")
        if st.button("Start Memory Chat", use_container_width=True):
            patient_id = st.session_state.user_data.get("patient_id", 12345678)
            session_id = create_chat_session(patient_id)
            if session_id:
                st.session_state.current_session_id = session_id
                st.success("Memory chat started!")
                st.rerun()
    
    # display preferences if available
    if st.session_state.patient_preferences:
        st.markdown("**Your Preferences:**")
        prefs = st.session_state.patient_preferences
        
        if prefs.get("preferred_times"):
            st.caption(f"Times: {', '.join(prefs['preferred_times'])}")
        if prefs.get("preferred_doctors"):
            st.caption(f"Doctors: {', '.join(prefs['preferred_doctors'])}")
    
    st.markdown("---")
    
    # system status and info
    st.markdown("### System Status")
    
    if st.session_state.api_status:
        st.success("Backend Connected ✅")
        st.info(f"Connected to: {BACKEND_URL}")
    else:
        st.error("Backend Disconnected ❌")
        st.warning(f"Please ensure the backend server is running on {BACKEND_URL}")
    
    st.markdown(f"**Session Messages:** {len(st.session_state.messages)}")
    
    # quick help
    st.markdown("### Quick Help")
    st.markdown("""
    **Memory Features:**
    - Enable memory to remember context
    - Create sessions for persistent chats
    - System learns your preferences
    
    **Getting Started:**
    1. Enable memory chat above
    2. Use forms or direct chat
    3. System remembers your preferences
    4. Continue conversations anytime
    """)

with col2:
    # display appropriate panel based on selected tab
    if st.session_state.current_tab == "Book Appointment":
        book_appointment_panel()
    elif st.session_state.current_tab == "Check Availability":
        check_availability_panel()
    elif st.session_state.current_tab == "Cancel/Reschedule":
        cancel_reschedule_panel()
    elif st.session_state.current_tab == "General Query":
        general_query_panel()
    
    # memory-powered chat interface (always visible)
    display_memory_chat_interface()