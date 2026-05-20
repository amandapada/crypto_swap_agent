import json
import logging
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GEMINI_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS, MAX_CONTEXT
from tools import tools, propose_swap_tool, propose_send_tool, report_transaction_status_tool, get_swap_quote_tool
from graph.state import AgentState
from graph.system_prompt import DEFAULT_SYSTEM_PROMPT

# 1. Setup Logger
logger = logging.getLogger(__name__)

# LLM Initialization
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=TEMPERATURE,
    max_output_tokens=MAX_OUTPUT_TOKENS,
    convert_system_message_to_human=False
).bind_tools(tools)

def agent_node(state: AgentState) -> AgentState:
    """The Brain: Decides what to do next."""
    messages = list(state["messages"])[-MAX_CONTEXT:]
    messages_with_system = [SystemMessage(content=DEFAULT_SYSTEM_PROMPT)] + messages
    
    try:
        response = llm.invoke(messages_with_system)
        return {"messages": [response]}
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return {"messages": [AIMessage(content="I'm having trouble thinking right now. Please try again.")]}

def get_swap_quote_node(state: AgentState) -> AgentState:
    """Executes the quote tool and returns raw data to the LLM."""
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    call_id = tool_call["id"] # Critical for linking result to call

    logger.info(f"Fetching Quote: {tool_call['args']}")
    
    try:
        result = get_swap_quote_tool.invoke(tool_call["args"])
        # Convert to JSON string so the LLM can read it
        content = json.dumps(result)
    except Exception as e:
        logger.error(f"Quote Tool Error: {e}")
        content = json.dumps({"error": str(e)})

    # Return a ToolMessage. The graph goes back to 'agent' after this.
    return {
        "messages": [ToolMessage(content=content, tool_call_id=call_id, name="get_swap_quote_tool")]
    }

def propose_swap_node(state: AgentState) -> AgentState:
    """Executes swap proposal logic."""
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    
    logger.info(f"Proposing Swap: {tool_call['args']}")
    
    # We still use invoke here to get the dict result
    result = propose_swap_tool.invoke(tool_call["args"])
    
    if result.get("error"):
        return {
            "messages": [AIMessage(content=f"Error: {result['error']}")],
            "proposed_transaction": None
        }
    
    # Construct a confirmation message
    # Note: Since this node goes to END, we return an AIMessage directly to the user
    msg = (
        f"I've prepared your swap:\n"
        f"• {result['amount']} {result['tokenIn']} ➡️ ~{result['estimatedOutput']} {result['tokenOut']}\n"
        f"• Chain: {result['chain']}\n"
        f"Please sign the transaction to proceed."
    )
    
    return {
        "messages": [AIMessage(content=msg)],
        "proposed_transaction": result # This updates the state for the API to read
    }

def propose_send_node(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]

    logger.info(f"Proposing Send: {tool_call['args']}")

    result = propose_send_tool.invoke(tool_call['args'])

    if result.get("error"):
        return {"messages": [AIMessage(content=result["error"])]}
    
    user_msg = f"Ready to send {result['amount']} {result['token']} to {result['toAddress']}. Please confirm."

    return {
        "messages": [AIMessage(content=user_msg)],
        "proposed_transaction": result
    }

def report_transaction_status_node(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    
    result = report_transaction_status_tool.invoke(tool_call["args"])
    return {"messages": [AIMessage(content=result)]}