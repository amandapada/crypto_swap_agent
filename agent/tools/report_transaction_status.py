from langchain_core.tools import tool

@tool
def report_transaction_status_tool(tx_hash: str, status: str, error: str = None) -> str:
    """Report the final status of a transaction to the user.

    Args:
        tx_hash: The transaction hash.
        status: Either "success" or "failure".
        error: Optional error message if status is "failure".

    Returns:
        User-friendly status message
    """

    if status == 'success':
        base_explorer = "https://basescan.org/tx/"
        return f"Transaction successful! View on Base Explorer: {base_explorer}{tx_hash}"
    else:
        error_guidance = {
            "insufficient funds": "You don't have enough tokens or ETH for gas. Add funds and try again.",
            "user rejected": "Transaction was canceled.",
            "gas too low": "Gas estimate was too low. Try increasing the gas limit.",
            "slippage": "Price moved beyond your slippage tolerance. Try increasing slippage or waiting for better market conditions.",            
        }

        guidance = "Please check the error and try again."
        for key, msg in error_guidance.items():
            if key in error.lower():
                guidance = msg
                break

        return f"X Transaction failed: {error}\n\n{guidance}"