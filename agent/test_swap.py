import requests
import os
import time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
# Base Sepolia RPC
RPC_URL = "https://sepolia.base.org" 
# Base Sepolia WETH Address (Required for ETH swaps on Uniswap V3)
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"

# Minimal ABI for Uniswap V3 SwapRouter 'exactInputSingle'
ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    }
]

def main():
    # 1. Get Private Key
    private_key = os.getenv("TEST_PRIVATE_KEY")
    if not private_key:
        print("❌ Error: TEST_PRIVATE_KEY not found in .env")
        return

    # 2. Call your Agent (Force it to give transaction data immediately)
    print("🤖 Asking Agent for swap proposal...")
    try:
        response = requests.post(
            "http://localhost:8001/chat", 
            json={
                "message": "Create a transaction to swap 0.0001 ETH for USDC immediately. Do not ask for confirmation.", 
                "conversation_id": "test-execution-force-1"
            }
        )
        response.raise_for_status()
        data = response.json()
        proposal = data.get("proposed_transaction")
        
        if not proposal:
            print(f"❌ No proposal returned. Agent said: {data['message']}")
            return

        print(f"✅ Proposal received: Swap {proposal['amount']} {proposal['tokenIn']} -> {proposal['tokenOut']}")

    except Exception as e:
        print(f"❌ API Error: {e}")
        return

    # 3. Setup Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    account = w3.eth.account.from_key(private_key)
    print(f"🔗 Connected to Base Sepolia. Wallet: {account.address}")

    # 4. Prepare Transaction Data
    # IMPORTANT: Uniswap V3 requires 'tokenIn' to be WETH address if input is ETH
    token_in = WETH_ADDRESS if proposal['tokenIn'].upper() == "ETH" else proposal['tokenInAddress']
    token_out = proposal['tokenOutAddress']
    amount_in_wei = w3.to_wei(float(proposal['amount']), 'ether')

    # Define the Swap Router Contract
    router_contract = w3.eth.contract(address=proposal['routerAddress'], abi=ROUTER_ABI)

    # Struct for exactInputSingle
    swap_params = (
        token_in,           # tokenIn
        token_out,          # tokenOut
        3000,               # fee (0.3% - standard pool)
        account.address,    # recipient
        int(time.time()) + 600, # deadline (10 mins)
        amount_in_wei,      # amountIn
        0,                  # amountOutMinimum (0 for testing, implies 100% slippage allowed)
        0                   # sqrtPriceLimitX96
    )

    # 5. Build Transaction
    print("📝 Building transaction...")
    try:
        tx = router_contract.functions.exactInputSingle(swap_params).build_transaction({
            'from': account.address,
            'value': amount_in_wei if proposal['tokenIn'].upper() == "ETH" else 0,
            'gas': 300000,
            'maxFeePerGas': w3.to_wei('2', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('1', 'gwei'),
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': 84532 # Base Sepolia Chain ID
        })
    except Exception as e:
        print(f"❌ Build Error (Check if you have ETH on Base Sepolia!): {e}")
        return

    # 6. Sign & Send
    print("✍️  Signing and sending...")
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f"🚀 Transaction sent! Hash: {tx_hash.hex()}")
    print(f"🔎 View on Blockscout: https://base-sepolia.blockscout.com/tx/{tx_hash.hex()}")

if __name__ == "__main__":
    main()