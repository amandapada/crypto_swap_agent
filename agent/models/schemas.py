from pydantic import BaseModel, Field
from typing import Union, Optional
from .transaction import SwapProposal, SendProposal

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's natural language input.")
    conversation_id: Optional[str] = Field(None, description="UUID or unique string to maintain chat history.")
    user_address: Optional[str] = Field(None, description="The connected wallet address (0x...) for context.")

class ChatResponse(BaseModel):
    message: str = Field(..., description="The agent's conversational text response.")
    proposed_transaction: Optional[Union[SwapProposal, SendProposal]] = Field(None, description="Structured transaction data if an action is proposed.")
    quote_data: Optional[dict] = Field(None, description="Raw price/quote data from the agent's internal tools.")
    conversation_id: str = Field(..., description="The ID of the session used.")