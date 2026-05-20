from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver # In Prod, use PostgresSaver
from .nodes import agent_node, propose_send_node, propose_swap_node, report_transaction_status_node, get_swap_quote_node
from .edges import should_continue
from .state import AgentState

# 1. Initialize Memory
memory = MemorySaver()

graph = StateGraph(AgentState)

# Nodes
graph.add_node("agent", agent_node)
graph.add_node("propose_swap", propose_swap_node)
graph.add_node("propose_send", propose_send_node)
graph.add_node("return_transaction_status", report_transaction_status_node)
graph.add_node("get_swap_quote", get_swap_quote_node)

graph.set_entry_point("agent")

# Edges
graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "get_swap_quote": "get_swap_quote",
        "propose_swap": "propose_swap",
        "propose_send": "propose_send",
        "return_transaction_status": "return_transaction_status",
        "end": END
    },
)

# 2. Logic Flow Updates
# Quotes go BACK to the agent so it can summarize the price to the user
graph.add_edge("get_swap_quote", "agent") 

# Proposals go to END (The user must confirm/sign on frontend)
graph.add_edge("propose_swap", END)
graph.add_edge("propose_send", END)
graph.add_edge("return_transaction_status", END)

# 3. Compile with Memory
app = graph.compile(checkpointer=memory)