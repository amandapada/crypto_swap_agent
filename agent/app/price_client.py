import requests
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

COINGECKO_IDS: Dict[str, str] = {
    "ETH": "ethereum",
    "WETH": "weth",
    "USDC": "usd-coin",
    "DAI": "dai",
    "USDT": "tether",
}

class PriceClient:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def get_token_price(self, token_symbol: str, vs_currency: str = "usd") -> Optional[float]:
        token_id = COINGECKO_IDS.get(token_symbol.upper())
        if not token_id:
            logger.warning(f"Token {token_symbol} not in CoinGecko mapping")
            return None

        try:
            resp = requests.get(
                f"{self.BASE_URL}/simple/price",
                params={"ids": token_id, "vs_currencies": vs_currency},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            price = data.get(token_id, {}).get(vs_currency)
            logger.info(f"Fetched price for {token_symbol}: {price}")
            return price
        except Exception as e:
            logger.error(f"Error fetching price for {token_symbol}: {e}")
            return None

    def estimate_swap_output(self, from_token: str, to_token: str, amount_in: float) -> Dict[str, any]:
        # ETH/WETH -> stable
        if from_token.upper() in ["ETH", "WETH"] and to_token.upper() in ["USDC", "DAI", "USDT"]:
            eth_price = self.get_token_price("ETH", "usd")
            if eth_price:
                estimated_output = amount_in * eth_price
                return {
                    "success": True,
                    "estimated_output": estimated_output,
                    "price": eth_price,
                    "from_token": from_token,
                    "to_token": to_token,
                    "source": "coingecko",
                }

        # stable -> ETH/WETH
        if from_token.upper() in ["USDC", "DAI", "USDT"] and to_token.upper() in ["ETH", "WETH"]:
            eth_price = self.get_token_price("ETH", "usd")
            if eth_price:
                estimated_output = amount_in / eth_price
                return {
                    "success": True,
                    "estimated_output": estimated_output,
                    "price": eth_price,
                    "from_token": from_token,
                    "to_token": to_token,
                    "source": "coingecko",
                }

        # general case
        from_price = self.get_token_price(from_token, "usd")
        to_price = self.get_token_price(to_token, "usd")
        if from_price and to_price:
            from_value_usd = amount_in * from_price
            estimated_output = from_value_usd / to_price
            return {
                "success": True,
                "estimated_output": estimated_output,
                "price": from_price / to_price,
                "from_token": from_token,
                "to_token": to_token,
                "source": "coingecko",
            }

        return {"success": False, "error": "Unable to fetch prices"}

price_client = PriceClient()
