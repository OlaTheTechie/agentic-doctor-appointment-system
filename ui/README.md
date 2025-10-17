# enhanced doctor appointment system ui

A comprehensive, professional Streamlit-based user interface for the Doctor Appointment Multi-Agent System.

## features

### book appointments
- Structured form with patient ID, doctor preferences, specialization
- Date and time selection with validation
- Additional notes for special requirements
- Real-time validation and error handling

### check availability 
- Search by doctor name, specialization, or date range
- Flexible time preferences (morning, afternoon, evening)
- Optional patient ID for personalized results

### ✏️ **Cancel/Reschedule**
- Cancel existing appointments with reason
- Reschedule to new dates and times
- Patient ID validation and appointment verification

### general queries
- Free-form questions about the system
- Quick action buttons for common queries
- Contextual help and examples

### professional design
- Medical-themed color scheme (blues, greens)
- Responsive layout for different screen sizes
- Clean, spacious design with proper typography
- Real-time backend connection status

### chat interface
- Conversation history with timestamps
- Distinct styling for user vs system messages
- Auto-scroll to latest messages
- Session management and reset functionality

## quick start

### prerequisites
1. **Backend API Running**: Ensure the FastAPI backend is running on `http://127.0.0.1:8000`
2. **Python Dependencies**: Streamlit and requests installed

### running the enhanced ui

#### option 1: using the run script (recommended)
```bash
cd backend/ui
python run_enhanced_app.py
```

#### option 2: direct streamlit command
```bash
cd backend/ui
streamlit run enhanced_app.py
```

The UI will open automatically in your browser at `http://localhost:8501`

## architecture

### component structure
```
Enhanced Streamlit App
├── Header (Status, Title, Connection Indicator)
├── Navigation Sidebar
│   ├── Tab Selection (Book, Check, Cancel, Query)
│   ├── System Status Display
│   └── Quick Help Section
├── Main Content Area
│   ├── Book Appointment Panel
│   ├── Check Availability Panel  
│   ├── Cancel/Reschedule Panel
│   └── General Query Panel
└── Chat Interface (Persistent)
    ├── Message History
    ├── Auto-scroll
    └── Reset Functionality
```

### session state management
- `messages`: Conversation history
- `current_tab`: Active panel selection
- `api_status`: Backend connection status
- `user_data`: Form input data
- `last_response`: Latest API response

## configuration

### api settings
```python
API_URL = "http://127.0.0.1:8000/execute"
REQUEST_TIMEOUT = 5  # seconds
```

### styling customization
The app uses custom CSS for medical theming. Key colors:
- Primary Blue: `#2563eb`
- Success Green: `#16a34a` 
- Warning Orange: `#ea580c`
- Error Red: `#ef4444`
- Background: `#f8fafc`

## usage guide

### 1. booking an appointment
1. select "book appointment" tab
2. Enter your Patient ID (7-8 digits)
3. Choose specialization (required)
4. Optionally specify doctor name
5. Select preferred date and time
6. Add any additional notes
7. Click "Book Appointment"

### 2. checking availability
1. select "check availability" tab
2. Optionally enter Patient ID for personalized results
3. Specify doctor name or specialization
4. Choose date range
5. Select time preference
6. Click "Check Availability"

### 3. Cancel/Reschedule
1. Select "✏️ Cancel/Reschedule" tab
2. Enter your Patient ID (required)
3. Choose "Cancel" or "Reschedule"
4. Provide current appointment details
5. If rescheduling, specify new date/time
6. Optionally add reason
7. Submit request

### 4. general queries
1. select "general query" tab
2. Use quick action buttons or type custom question
3. Optionally include Patient ID
4. Click "Send Query"

## validation & error handling

### input validation
- **Patient ID**: Must be 7-8 digits
- **Dates**: Cannot be in the past
- **Required Fields**: Clear error messages for missing data
- **API Connectivity**: Real-time status checking

### error types
- **success**: green notifications for successful operations
- **error**: red notifications for failures with clear explanations
- **warning**: yellow notifications for missing information
- **info**: blue notifications for general information

## backend integration

### api request format
```json
{
    "id_number": 12345678,
    "messages": [
        {"role": "user", "content": "I want to book an appointment"}
    ],
    "intent": "book_appointment",
    "query": "Book appointment for cardiology on 2024-12-01"
}
```

### response handling
- Parses API responses automatically
- Displays system messages in chat interface
- Handles connection errors gracefully
- Provides user-friendly error messages

## troubleshooting

### common issues

#### "Repeated routing detected" Error
- **Symptom**: Backend logs show "Repeated routing detected. Ending conversation."
- **Solution**: ✅ **FIXED** - Enhanced UI now handles this automatically
- **Features**: Auto-detection, conversation reset, user guidance
- **See**: `TROUBLESHOOTING.md` for detailed information

#### backend connection failed
- **Symptom**: Red "Backend Disconnected" status
- **Solution**: Ensure FastAPI server is running on port 8000
- **Check**: Visit `http://127.0.0.1:8000/docs` in browser

#### invalid patient id
- **Symptom**: "Please enter a valid Patient ID" error
- **Solution**: Use 7-8 digit numbers only (e.g., 1234567 or 12345678)

#### request timeout
- **Symptom**: "Request timed out" message
- **Solution**: Check backend server performance and network connection

#### form validation errors
- **Symptom**: Red error messages on form submission
- **Solution**: Fill all required fields marked with *

### testing the enhanced ui

Run the test suite to verify everything works correctly:
```bash
cd backend/ui
python test_enhanced_ui.py
```

This will test:
- Backend API connectivity
- Simple queries
- Appointment booking
- Conversation flow (anti-loop protection)

### debug mode
The enhanced UI includes built-in debug logging. Check the terminal where you're running Streamlit for detailed API request/response information.

For additional debugging, see `TROUBLESHOOTING.md` for comprehensive solutions.

## deployment

### local development
```bash
# start backend
cd backend
python main.py

# start enhanced ui (in new terminal)
cd backend/ui
python run_enhanced_app.py
```

### production considerations
- Use environment variables for API_URL
- Add authentication if required
- Configure proper CORS settings
- Use HTTPS in production
- Add logging and monitoring

## customization

### adding new panels
1. Create new panel function following the pattern:
```python
def new_panel():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    # Panel content here
    st.markdown('</div>', unsafe_allow_html=True)
```

2. Add to navigation tabs list
3. Add to main panel display logic

### styling changes
Modify the CSS in the `st.markdown()` section at the top of `enhanced_app.py`

### api integration
Update the `send_api_request()` function to modify request format or add new endpoints

## performance

### optimization features
- Session state for maintaining data across interactions
- Efficient API request handling with timeouts
- Minimal re-renders with strategic `st.rerun()` usage
- Lazy loading of components

### resource usage
- Lightweight Streamlit application
- Minimal external dependencies
- Efficient CSS and HTML rendering
- Optimized for responsive design

## 🤝 Contributing

To contribute improvements:
1. Follow the existing code structure
2. Maintain the medical theme and professional styling
3. Add proper error handling for new features
4. Update this README for any new functionality
5. Test with the backend API thoroughly

## license

This enhanced UI is part of the Doctor Appointment Multi-Agent System project.