from langchain_core.tools import tool
from app.tokens import get_token_address
from decimal import Decimal, InvalidOperation
import re

@tool 
def propose_send_tool(token: str, recipient_address: str, amount: str):
    """Propose a token send transaction on base.
    
    Args:
        token: Token symbol to send.
        recipient_address: The Recipient's wallet address (0x...).
        amount: The amount to send as a STRING.
    """
    # 1. Validate Address
    if not re.match(r"^0x[a-fA-F0-9]{40}$", recipient_address):
        return {"error": "Invalid recipient address format.", "action": "error"}

    # 2. Validate Amount
    try:
        amount_d = Decimal(amount)
        if amount_d <= 0:
             return {"error": "Amount must be positive", "action": "error"}
    except InvalidOperation:
        return {"error": f"Invalid amount format: {amount}", "action": "error"}

    # 3. Resolve Token
    token_address = get_token_address(token)
    if not token_address:
        return {"error": f"Unknown token: {token}", "action": "error"}
    
    return {
        "action": "send",
        "toAddress": recipient_address,
        "token": token,
        "tokenAddress": token_address,
        "amount": str(amount_d),
        "chain": "base"
    }