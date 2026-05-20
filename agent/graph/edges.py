from graph.state import AgentState
import logging

logger = logging.getLogger(__name__)

def should_continue(state: AgentState) -> str:
    last_message = state['messages'][-1]

    # Safety check
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
       return "end" 
  
    tool_name = last_message.tool_calls[0]["name"]
    
    logger.info(f"Routing to tool: {tool_name}")

    if tool_name == "get_swap_quote_tool": 
        return "get_swap_quote"
    elif tool_name == "propose_swap_tool":
      return "propose_swap"  
    elif tool_name == "propose_send_tool":
      return "propose_send"  
    elif tool_name == "report_transaction_status_tool":
      return "return_transaction_status"  

    logger.warning(f"Unknown tool call detected: {tool_name}")
    return "end"