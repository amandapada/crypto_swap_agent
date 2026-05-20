from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from models.schemas import ChatRequest, ChatResponse
import logging
from graph import app as agent_app

# 1. Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Miye Swap Agent API",
    description="Conversational AI Agent for Token Swaps and Sends on Base Network.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse, summary="Send a message to the Miye Agent")
async def chat(request: ChatRequest):
    """
    Main conversational endpoint. 
    Processes user text and returns either a direct reply or a structured transaction proposal (swap/send).
    """
    logger.info(f"Incoming: {request.message} (ID: {request.conversation_id})")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    # 3. LangGraph Config for Memory
    # Use conversation_id as thread_id for state persistence
    conv_id = request.conversation_id or "default_user"
    config = {"configurable": {"thread_id": conv_id}}
    
    # 4. Input only needs the NEW message
    input_state = {"messages": [HumanMessage(content=request.message)]}

    try:
        # 5. ASYNC Execution (ainvoke)
        final_state = await agent_app.ainvoke(input_state, config=config)
        
        # Extract the last message content
        last_msg = final_state["messages"][-1]
        response_text = last_msg.content
        
        # Extract transaction if it exists in state
        transaction = final_state.get("proposed_transaction")

        return ChatResponse(
            message=response_text,
            proposed_transaction=transaction,
            conversation_id=conv_id
        )

    except Exception as e:
        logger.exception("Agent execution failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", summary="API Health Check")
async def health():
    return {"status": "healthy"}