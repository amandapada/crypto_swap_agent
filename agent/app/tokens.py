# Base network token registry
BASE_TOKENS = {
    "ETH": {
        "address": "0x0000000000000000000000000000000000000000",
        "decimals": 18,
        "name": "Ethereum"
    },
    "USDC": {
        "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "decimals": 6,
        "name": "USD Coin"
    },
    "WETH": {
        "address": "0x4200000000000000000000000000000000000006",
        "decimals": 18,
        "name": "Wrapped Ether"
    },
    "DAI": {
        "address": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
        "decimals": 18,
        "name": "Dai Stablecoin"
    }
}

def get_token_address(symbol: str) -> str:
    """Helper to get token address by symbol."""
    token = BASE_TOKENS.get(symbol.upper())
    if token:
        return token["address"]
    return None