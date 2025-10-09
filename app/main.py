from fastapi import FastAPI
from app.routes.agent_routes import router as agent_router

app = FastAPI(title="Doctor Appointment Agent API")
app.include_router(agent_router)