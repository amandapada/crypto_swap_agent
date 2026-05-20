from pydantic import BaseModel, Field, field_validator
import re

class SwapProposal(BaseModel):
    action: str = Field("swap", description="Identifies this as a swap transaction.")
    tokenIn: str = Field(..., description="Symbol of the token to sell (e.g., ETH).")
    tokenInAddress: str = Field(..., description="Contract address of the token to sell.")
    tokenOut: str = Field(..., description="Symbol of the token to buy (e.g., USDC).")
    tokenOutAddress: str = Field(..., description="Contract address of the token to buy.")
    amount: str = Field(..., description="Amount to swap as a string to preserve precision.")
    estimatedOutput: str = Field(..., description="Estimated amount of tokenOut to be received.")
    maxSlippage: str = Field(..., description="Maximum allowed slippage percentage.")
    chain: str = Field("base", description="The network chain ID or name (default: base).")
    routerAddress: str = Field(..., description="The address of the Uniswap/Router contract to call.")

class SendProposal(BaseModel):
    action: str = Field("send", description="Identifies this as a token send transaction.")
    token: str = Field(..., description="Symbol of the token to send.")
    tokenAddress: str = Field(..., description="Contract address of the token to send.")
    toAddress: str = Field(..., description="Recipient wallet address (0x...).")
    amount: str = Field(..., description="Amount to send as a string.")
    chain: str = Field("base", description="The network chain ID or name.")

    @field_validator('toAddress')
    @classmethod
    def validate_address(cls, v: str) -> str:
        # Strictly enforce 0x + 40 hex characters
        if not re.match(r"^0x[a-fA-F0-9]{40}$", v):
            raise ValueError(f"Invalid Ethereum address: {v}. Must start with 0x followed by 40 hex characters.")
        return v