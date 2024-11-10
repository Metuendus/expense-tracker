from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence, List, Dict, Optional

class Expense(TypedDict):
    amount: float
    description: str
    date: str
    category: Optional[str]

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]