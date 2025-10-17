"""
multi-agent system for doctor appointment management
clean architecture with specialized agents and proper state management
"""

from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass
from datetime import datetime, date
import json

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from ..utils.llm import LLM
from ..utils.logger import get_logger, log_agent_activity, log_error
from ..toolkit.appointment_tools import set_appointment, cancel_appointment, reschedule_appointment
from ..toolkit.availability_tools import check_availability_by_doctor, check_availability_by_specialisation


# ============================================================================
# state management
# ============================================================================

@dataclass
class ConversationState:
    """Clean state management for the multi-agent system"""
    
    # core conversation data
    messages: List[BaseMessage]
    patient_id: int
    
    # current request context
    current_intent: Optional[str] = None
    current_query: str = ""
    
    # agent coordination
    active_agent: Optional[str] = None
    agent_response: Optional[str] = None
    
    # workflow control
    step_count: int = 0
    max_steps: int = 10
    is_complete: bool = False
    
    # error handling
    last_error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for LangGraph"""
        return {
            "messages": self.messages,
            "patient_id": self.patient_id,
            "current_intent": self.current_intent,
            "current_query": self.current_query,
            "active_agent": self.active_agent,
            "agent_response": self.agent_response,
            "step_count": self.step_count,
            "is_complete": self.is_complete,
            "last_error": self.last_error,
            "retry_count": self.retry_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationState':
        """Create state from dictionary"""
        return cls(
            messages=data.get("messages", []),
            patient_id=data.get("patient_id", 0),
            current_intent=data.get("current_intent"),
            current_query=data.get("current_query", ""),
            active_agent=data.get("active_agent"),
            agent_response=data.get("agent_response"),
            step_count=data.get("step_count", 0),
            is_complete=data.get("is_complete", False),
            last_error=data.get("last_error"),
            retry_count=data.get("retry_count", 0)
        )


# ============================================================================
# intent classification
# ============================================================================

class IntentClassifier:
    """Classifies user intents for proper agent routing"""
    
    def __init__(self, llm):
        self.llm = llm
        
    def classify_intent(self, query: str, context: List[BaseMessage]) -> Dict[str, Any]:
        """Classify user intent from query and conversation context"""
        
        classification_prompt = """
        You are an intent classifier for a doctor appointment system.
        
        Analyze the user's query and classify it into one of these intents:
        
        1. **check_availability** - User wants to check doctor/appointment availability
           Examples: "Is Dr. Smith available?", "What doctors are free today?", "Check availability"
        
        2. **book_appointment** - User wants to book a new appointment
           Examples: "Book an appointment", "I need to see a doctor", "Schedule me with Dr. Jones"
        
        3. **cancel_appointment** - User wants to cancel an existing appointment
           Examples: "Cancel my appointment", "I need to cancel", "Remove my booking"
        
        4. **reschedule_appointment** - User wants to change an existing appointment
           Examples: "Reschedule my appointment", "Change my booking", "Move my appointment"
        
        5. **general_inquiry** - General questions about the system, doctors, services
           Examples: "What services do you offer?", "How does this work?", "Tell me about doctors"
        
        6. **greeting** - Simple greetings or unclear requests
           Examples: "Hello", "Hi", "Help me", unclear requests
        
        Respond with JSON format:
        {
            "intent": "intent_name",
            "confidence": 0.95,
            "reasoning": "Brief explanation of classification",
            "extracted_entities": {
                "doctor_name": "extracted doctor name if any",
                "date": "extracted date if any", 
                "specialization": "extracted specialization if any"
            }
        }
        
        User Query: "{query}"
        """
        
        try:
            messages = [
                SystemMessage(content=classification_prompt.format(query=query)),
                HumanMessage(content=f"Classify this query: {query}")
            ]
            
            response = self.llm.invoke(messages)
            
            # parse json response
            try:
                # clean the response content
                content = response.content.strip()
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                
                result = json.loads(content)
                return result
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                # fallback classification
                return self._fallback_classification(query)
                
        except Exception as e:
            print(f"Intent classification error: {e}")
            return self._fallback_classification(query)
    
    def _fallback_classification(self, query: str) -> Dict[str, Any]:
        """Simple rule-based fallback classification"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["available", "availability", "free", "open"]):
            return {"intent": "check_availability", "confidence": 0.8, "reasoning": "Fallback: availability keywords"}
        elif any(word in query_lower for word in ["book", "schedule", "appointment", "see doctor"]):
            return {"intent": "book_appointment", "confidence": 0.8, "reasoning": "Fallback: booking keywords"}
        elif any(word in query_lower for word in ["cancel", "remove", "delete"]):
            return {"intent": "cancel_appointment", "confidence": 0.8, "reasoning": "Fallback: cancel keywords"}
        elif any(word in query_lower for word in ["reschedule", "change", "move", "modify"]):
            return {"intent": "reschedule_appointment", "confidence": 0.8, "reasoning": "Fallback: reschedule keywords"}
        else:
            return {"intent": "general_inquiry", "confidence": 0.6, "reasoning": "Fallback: default classification"}


# ============================================================================
# specialized agents
# ============================================================================

class AvailabilityAgent:
    """Specialized agent for checking doctor and appointment availability"""
    
    def __init__(self, llm):
        self.llm = llm
        self.tools = [check_availability_by_doctor, check_availability_by_specialisation]
        self.agent = create_react_agent(self.llm, self.tools)
    
    def process_request(self, state: ConversationState) -> str:
        """Process availability check requests"""
        try:
            # prepare context for the agent
            system_msg = SystemMessage(content="""
            You are a specialized availability checking agent for a doctor appointment system.
            
            Your job is to help users check doctor availability using the available tools.
            
            Key guidelines:
            - Use check_availability_by_doctor when user mentions a specific doctor name
            - Use check_availability_by_specialisation when user asks about a medical specialty
            - Always ask for missing required information (date, doctor name, or specialization)
            - Provide clear, helpful responses about availability in a simple, readable format
            - If no availability found, suggest alternatives
            - Format responses for easy reading in a chat interface (avoid complex tables)
            
            IMPORTANT: When using tools, always format dates as DD-MM-YYYY (e.g., 16-10-2025).
            
            Response formatting guidelines:
            - Keep responses simple and clean - avoid markdown formatting
            - Use plain text with simple punctuation
            - List times in a readable format like "08:00, 08:30, 09:00"
            - Be conversational and friendly
            - Avoid special characters, bold text, or complex formatting
            
            Current date: {current_date}
            Patient ID: {patient_id}
            
            Available doctors (use exact names): kevin anderson, robert martinez, susan davis, 
            daniel miller, sarah wilson, michael green, lisa brown, jane smith, emily johnson, john doe
            """.format(
                current_date=date.today().strftime("%d-%m-%Y"),
                patient_id=state.patient_id
            ))
            
            # build message history
            messages = [system_msg] + state.messages[-5:]  # Last 5 messages for context
            
            # execute the agent
            result = self.agent.invoke({"messages": messages})
            
            # extract the response
            if result.get("messages"):
                return result["messages"][-1].content
            else:
                return "I'm having trouble checking availability right now. Please try again."
                
        except Exception as e:
            print(f"AvailabilityAgent error: {e}")
            return f"I encountered an error while checking availability: {str(e)}"


class BookingAgent:
    """Specialized agent for booking, canceling, and rescheduling appointments"""
    
    def __init__(self, llm):
        self.llm = llm
        self.tools = [set_appointment, cancel_appointment, reschedule_appointment]
        self.agent = create_react_agent(self.llm, self.tools)
    
    def process_request(self, state: ConversationState) -> str:
        """Process booking-related requests"""
        try:
            # determine the specific booking action
            intent = state.current_intent
            
            if intent == "book_appointment":
                system_content = """
                You are a specialized appointment booking agent.
                
                Your job is to help users book new appointments using the set_appointment tool.
                
                Required information for booking:
                - Patient ID (already provided: {patient_id})
                - Doctor name (must be exact match from available doctors)
                - Date and time (format: DD-MM-YYYY HH:MM)
                
                Available doctors: kevin anderson, robert martinez, susan davis, daniel miller, 
                sarah wilson, michael green, lisa brown, jane smith, emily johnson, john doe
                
                Always confirm all details before booking and provide clear confirmation.
                """
                
            elif intent == "cancel_appointment":
                system_content = """
                You are a specialized appointment cancellation agent.
                
                Your job is to help users cancel existing appointments using the cancel_appointment tool.
                
                Required information for cancellation:
                - Patient ID (already provided: {patient_id})
                - Doctor name
                - Appointment date and time
                
                Always confirm the cancellation details and provide clear confirmation.
                """
                
            elif intent == "reschedule_appointment":
                system_content = """
                You are a specialized appointment rescheduling agent.
                
                Your job is to help users reschedule existing appointments using the reschedule_appointment tool.
                
                Required information for rescheduling:
                - Patient ID (already provided: {patient_id})
                - Doctor name
                - Current appointment date and time
                - New desired date and time
                
                Always confirm both old and new appointment details.
                """
            else:
                system_content = """
                You are a booking assistant. Help the user with their appointment-related request.
                Patient ID: {patient_id}
                """
            
            system_msg = SystemMessage(content=system_content.format(patient_id=state.patient_id))
            
            # build message history
            messages = [system_msg] + state.messages[-5:]
            
            # execute the agent
            result = self.agent.invoke({"messages": messages})
            
            # extract the response
            if result.get("messages"):
                return result["messages"][-1].content
            else:
                return "I'm having trouble processing your booking request. Please try again."
                
        except Exception as e:
            print(f"BookingAgent error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"


class GeneralAssistantAgent:
    """General assistant for inquiries, greetings, and system information"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def process_request(self, state: ConversationState) -> str:
        """Process general inquiries and provide system information"""
        try:
            system_msg = SystemMessage(content="""
            You are a helpful assistant for a doctor appointment system.
            
            You help users with:
            - General information about the appointment system
            - Explaining how to book, cancel, or reschedule appointments
            - Providing information about available doctors and specializations
            - Answering questions about the system
            - Greeting users and guiding them to the right services
            
            Available doctors: Kevin Anderson, Robert Martinez, Susan Davis, Daniel Miller, 
            Sarah Wilson, Michael Green, Lisa Brown, Jane Smith, Emily Johnson, John Doe
            
            Available specializations: General Dentist, Cosmetic Dentist, Prosthodontist, 
            Pediatric Dentist, Emergency Dentist, Oral Surgeon, Orthodontist
            
            Be helpful, friendly, and guide users to the appropriate actions.
            Patient ID: {patient_id}
            """.format(patient_id=state.patient_id))
            
            # build message history
            messages = [system_msg] + state.messages[-3:]
            
            # get response from llm
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            print(f"GeneralAssistantAgent error: {e}")
            return "Hello! I'm here to help you with doctor appointments. How can I assist you today?"


# ============================================================================
# multi-agent orchestrator
# ============================================================================

class MultiAgentOrchestrator:
    """Main orchestrator that coordinates all specialized agents"""
    
    def __init__(self):
        # initialize llm
        llm_instance = LLM()
        self.llm = llm_instance.get_model()
        
        # initialize components
        self.intent_classifier = IntentClassifier(self.llm)
        self.availability_agent = AvailabilityAgent(self.llm)
        self.booking_agent = BookingAgent(self.llm)
        self.general_agent = GeneralAssistantAgent(self.llm)
        
        # build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> CompiledStateGraph:
        """Build the LangGraph workflow"""
        
        # define the state graph
        graph = StateGraph(dict)  # Use dict for flexibility
        
        # add nodes
        graph.add_node("classify_intent", self._classify_intent_node)
        graph.add_node("availability_agent", self._availability_agent_node)
        graph.add_node("booking_agent", self._booking_agent_node)
        graph.add_node("general_agent", self._general_agent_node)
        graph.add_node("finalize_response", self._finalize_response_node)
        
        # define edges
        graph.add_edge(START, "classify_intent")
        
        # conditional routing from intent classification
        graph.add_conditional_edges(
            "classify_intent",
            self._route_to_agent,
            {
                "availability": "availability_agent",
                "booking": "booking_agent", 
                "general": "general_agent"
            }
        )
        
        # all agents go to finalize
        graph.add_edge("availability_agent", "finalize_response")
        graph.add_edge("booking_agent", "finalize_response")
        graph.add_edge("general_agent", "finalize_response")
        graph.add_edge("finalize_response", END)
        
        return graph.compile()
    
    def _classify_intent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for intent classification"""
        conv_state = ConversationState.from_dict(state)
        
        # get the latest user message
        user_messages = [msg for msg in conv_state.messages if isinstance(msg, HumanMessage)]
        if not user_messages:
            conv_state.current_intent = "general_inquiry"
            conv_state.current_query = "Hello"
        else:
            latest_query = user_messages[-1].content
            conv_state.current_query = latest_query
            
            # classify intent
            classification = self.intent_classifier.classify_intent(latest_query, conv_state.messages)
            conv_state.current_intent = classification.get("intent", "general_inquiry")
        
        conv_state.step_count += 1
        return conv_state.to_dict()
    
    def _route_to_agent(self, state: Dict[str, Any]) -> str:
        """Route to appropriate agent based on intent"""
        intent = state.get("current_intent", "general_inquiry")
        
        if intent in ["check_availability"]:
            return "availability"
        elif intent in ["book_appointment", "cancel_appointment", "reschedule_appointment"]:
            return "booking"
        else:
            return "general"
    
    def _availability_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for availability agent processing"""
        conv_state = ConversationState.from_dict(state)
        conv_state.active_agent = "availability"
        
        try:
            response = self.availability_agent.process_request(conv_state)
            conv_state.agent_response = response
        except Exception as e:
            conv_state.agent_response = f"I'm sorry, I encountered an error checking availability: {str(e)}"
            conv_state.last_error = str(e)
        
        return conv_state.to_dict()
    
    def _booking_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for booking agent processing"""
        conv_state = ConversationState.from_dict(state)
        conv_state.active_agent = "booking"
        
        try:
            response = self.booking_agent.process_request(conv_state)
            conv_state.agent_response = response
        except Exception as e:
            conv_state.agent_response = f"I'm sorry, I encountered an error with your booking request: {str(e)}"
            conv_state.last_error = str(e)
        
        return conv_state.to_dict()
    
    def _general_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for general assistant processing"""
        conv_state = ConversationState.from_dict(state)
        conv_state.active_agent = "general"
        
        try:
            response = self.general_agent.process_request(conv_state)
            conv_state.agent_response = response
        except Exception as e:
            conv_state.agent_response = "Hello! I'm here to help you with doctor appointments. How can I assist you today?"
            conv_state.last_error = str(e)
        
        return conv_state.to_dict()
    
    def _finalize_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for finalizing the response"""
        conv_state = ConversationState.from_dict(state)
        
        # add the agent response to messages
        if conv_state.agent_response:
            conv_state.messages.append(AIMessage(content=conv_state.agent_response))
        
        conv_state.is_complete = True
        return conv_state.to_dict()
    
    def process_request(self, patient_id: int, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Main entry point for processing requests"""
        
        # initialize state
        initial_state = ConversationState(
            messages=messages,
            patient_id=patient_id
        )
        
        try:
            # execute the workflow
            result = self.workflow.invoke(initial_state.to_dict())
            
            # return the final state
            return result
            
        except Exception as e:
            print(f"MultiAgentOrchestrator error: {e}")
            
            # return error response
            error_response = ConversationState(
                messages=messages + [AIMessage(content=f"I'm sorry, I encountered an error: {str(e)}")],
                patient_id=patient_id,
                is_complete=True,
                last_error=str(e)
            )
            
            return error_response.to_dict()


# ============================================================================
# main agent class (for backward compatibility)
# ============================================================================

class AppointmentAgent:
    """Main agent class that uses the multi-agent system"""
    
    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()
    
    def workflow(self):
        """Return the workflow for external use"""
        return self.orchestrator.workflow
    
    def process_query(self, patient_id: int, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Process a query using the multi-agent system"""
        return self.orchestrator.process_request(patient_id, messages)