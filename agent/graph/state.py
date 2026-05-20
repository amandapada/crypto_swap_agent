from typing import TypedDict, Annotated, Any, Sequence, Optional, Dict
from typing_extensions import NotRequired
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class AgentState(TypedDict):
    """This represents the state of the agent's workflow."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    proposed_transaction: NotRequired[Optional[Dict[str, Any]]]
    context_memory: NotRequired[dict]