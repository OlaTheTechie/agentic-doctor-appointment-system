# doctors-appointment-agent
A multi-agent healthcare assistant that books, manages, and optimizes doctor appointments effortlessly

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)
![LangChain](https://img.shields.io/badge/LangChain-Agent-yellow)


## Overview

Doctor Appointment Agent is an intelligent agent that simplifies the process of scheduling medical appointments.  
Users can chat naturally (e.g., *"Book me a dentist appointment next Tuesday"*) and the system automatically handles the reasoning, slot-filling, and booking logic behind the scenes.


## Features
- Natural conversational agent for doctor appointment scheduling
- Smart reasoning to extract patient intent and appointment details from api requests
- Supports multiple query types (information requests, booking requests). All can be sent to the same enpoint
- FastAPI backend with structured agent state tracking
- Easily extendable with new specializations or appointment logic


## Tech Stack
- **Backend:** FastAPI, Python 3.10
- **AI Agent:** LangChain, OpenAI API
- **Data Models:** Pydantic, TypedDict
- **Frontend (coming soon):** React, TailwindCSS

## Installation
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
