from typing import TypedDict, List, Literal, Any, Annotated
from langgraph.graph.message import add_messages


class Router(TypedDict): 
    next: Literal["information_node", "booking_node", "FINISH"]
    reasoning: str


class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    id_number: int
    next: str
    query: str
    current_reasoning: str
    step_count: int
