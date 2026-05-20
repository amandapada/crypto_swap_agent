from langchain_core.tools import tool
from app.tokens import get_token_address
from app.price_client import price_client
from app.config import UNISWAP_ROUTER_ADDRESS
from decimal import Decimal, InvalidOperation

@tool
def propose_swap_tool(from_token: str, to_token: str, amount: str, slippage: str = "1.0") -> dict:
    """Propose a token swap transaction.
    
    Args:
        from_token: Token symbol to swap from (e.g., ETH).
        to_token: Token symbol to swap to (e.g., USDC).
        amount: Amount to swap as a STRING (e.g., "0.1", "100").
        slippage: Max slippage tolerance percentage as a string (default "1.0").
    """
    # 1. Validate Input Math
    try:
        amount_d = Decimal(amount)
        slippage_d = Decimal(slippage)
        if amount_d <= 0:
            return {"error": "Amount must be positive", "action": "error"}
    except InvalidOperation:
        return {"error": f"Invalid number format for amount: {amount}", "action": "error"}

    # 2. Resolve Addresses
    from_address = get_token_address(from_token)
    to_address = get_token_address(to_token)
    
    if not from_address or not to_address:
        unknown = []
        if not from_address: unknown.append(from_token)
        if not to_address: unknown.append(to_token)
        return {
            "error": f"Unknown tokens: {', '.join(unknown)}",
            "action": "error"
        }
    
    # 3. Get Quote (using float for estimation only, not transaction data)
    quote = price_client.estimate_swap_output(from_token, to_token, float(amount_d))
    
    if not quote.get("success"):
        return {
            "error": "Unable to fetch current price quote. Please try again.",
            "action": "error"
        }
    
    return {
        "action": "swap",
        "tokenIn": from_token,
        "tokenInAddress": from_address,
        "tokenOut": to_token,
        "tokenOutAddress": to_address,
        "amount": str(amount_d), # Return normalized string
        "estimatedOutput": f"{quote['estimated_output']:.6f}",
        "maxSlippage": str(slippage_d),
        "chain": "base",
        "routerAddress": UNISWAP_ROUTER_ADDRESS, 
        "note": "Quote from CoinGecko market data."
    }