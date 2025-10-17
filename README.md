# doctors-appointment-agent
A multi-agent healthcare assistant that books, manages, and optimizes doctor appointments effortlessly

![Project Screenshot](/assets/images/automate-doctors-appointment-with-ai-agents-2.jpg)


## overview

Doctor Appointment Agent is an intelligent agent that simplifies the process of scheduling medical appointments.  
Users can chat naturally (e.g., *"Book me a dentist appointment next Tuesday"*) and the system automatically handles the reasoning, slot-filling, and booking logic behind the scenes.


## features
- Natural conversational agent for doctor appointment scheduling
- Smart reasoning to extract patient intent and appointment details from api requests
- Supports multiple query types (information requests, booking requests). All can be sent to the same enpoint
- FastAPI backend with structured agent state tracking
- Easily extendable with new specializations or appointment logic
- Uses LangGraph for agent logic


## tech stack
- **Backend:** FastAPI, Python 3.10
- **AI Agent:** LangChain, OpenAI API
- **Data Models:** Pydantic, TypedDict
- **Frontend (coming soon):** React, TailwindCSS

## installation
1. Clone the repository
```bash
git clone https://github.com/OlaTheTechie/doctors-appointment-agent
.git
cd doctors-appointment-agent

2. Install dependencies with poetry
poetry install 

3. Activate virtual environment

4. Run the app 
uvicorn main:app --reload
```

## usage

### example api request
```bash 
curl -X POST "http://localhost:8000/execute" \
     -H "Content-Type: application/json" \
     -d '
        {
            "id_number": 12345678,
            "intent": "book_appointment",
            "messages": [
                {"role": "user", "content": "i want to book an appointment with Dr. Adams tomorrow morning"}
            ],
            "details": {
                "patient_name": "John Doe",
                "doctor_name": "Dr. Adams",
                "date": "10-10-2025",
                "time": "09:00"
            }
        }
     '
```

### example response
```bash
{
    "id_number": 12345678,
    "intent": "book_appointment",
    "details": {
        "patient_name": "John Doe",
        "doctor_name": "Dr. Adams",
        "specialisation": null,
        "date": "10-10-2025",
        "time": "09:00",
        "appointment_id": null
    },
    "messages": [
        {
            "role": "human",
            "content": "i want to book an appointment with Dr. Adams tomorrow morning",
            "name": null
        },
        {
            "role": "human",
            "content": "user's identification number is 12345678",
            "name": null
        },
        {
            "role": "human",
            "content": "i want to book an appointment with Dr. Adams tomorrow morning",
            "name": null
        },
        {
            "role": "human",
            "content": "user's identification number is 12345678",
            "name": null
        },
        {
            "role": "ai",
            "content": "I’m sorry, but **Dr. Adams isn’t one of the doctors we have available for scheduling**. Here are the doctors you can book with:\n\n- Kevin Anderson  \n- Robert Martinez  \n- Susan Davis  \n- Daniel Miller  \n- Sarah Wilson  \n- Michael Green  \n- Lisa Brown  \n- Jane Smith  \n- Emily Johnson  \n- John Doe  \n\nCould you let me know which of these doctors you’d like to see tomorrow morning? Once you pick one, I can go ahead and schedule the appointment for you.",
            "name": null
        }
    ],
    "next": "FINISH",
    "current_reasoning": "User wants to book an appointment with Dr. Adams tomorrow morning, which is a booking action."
}
```


## future improvements
```markdown
- [ ] Add real-time database integration (PostgreSQL)
- [ ] Add user authentication
- [ ] Build React-based conversational UI
- [ ] Integrate calendar and reminders
```

## contributing
Pull requests are welcome!  
For major changes, please open an issue first to discuss what you’d like to change.


## license
This project is licensed under the MIT License.
