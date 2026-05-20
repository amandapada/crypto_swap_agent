from langchain_core.tools import tool
from app.tokens import get_token_address
from app.price_client import price_client

@tool
def get_swap_quote_tool(from_token: str, to_token: str, amount: float) -> dict:
    """Get a price quote for swapping tokens using market prices (CoinGecko)."""
    from_address = get_token_address(from_token)
    to_address = get_token_address(to_token)

    if not from_address or not to_address:
        unknown = []
        if not from_address:
            unknown.append(from_token)
        if not to_address:
            unknown.append(to_token)
        return {
            "error": f"Unknown tokens: {', '.join(unknown)}",
            "action": "error",
        }

    quote = price_client.estimate_swap_output(from_token, to_token, amount)

    if not quote.get("success"):
        return {
            "error": "Unable to fetch current prices. Please try again.",
            "action": "error",
        }

    return {
        "action": "quote",
        "success": True,
        "from_token": from_token,
        "to_token": to_token,
        "amount_in": str(amount),
        "estimated_output": f"{quote['estimated_output']:.6f}",
        "price": f"{quote['price']:.4f}",
        "source": "coingecko",
        "note": "Price from market data. Actual swap may vary slightly.",
    }
