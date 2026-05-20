import sys
import os

# Ensure the app module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.price_client import price_client

def test_prices():
    print("Testing CoinGecko API Integration...\n")
    
    # Test 1: Get ETH price
    print("Test 1: Fetching ETH price")
   
    eth_price = price_client.get_token_price("ETH")
    if eth_price:
        print(f"✓ ETH Price: ${eth_price:,.2f}\n")
    else:
        print("✗ Failed to fetch ETH price\n")
    
    # Test 2: Get USDC price
    print("Test 2: Fetching USDC price")
    usdc_price = price_client.get_token_price("USDC")
    if usdc_price:
        print(f"✓ USDC Price: ${usdc_price:.4f}\n")
    else:
        print("✗ Failed to fetch USDC price\n")
    
    # Test 3: Estimate swap (1 ETH -> USDC)
    print("Test 3: Estimating swap: 1 ETH → USDC")
  
    quote = price_client.estimate_swap_output("ETH", "USDC", 1.0)
    if quote.get("success"):
        print(f"✓ Input: 1 ETH")
        print(f"✓ Estimated Output: {quote['estimated_output']:.2f} USDC")
       
        price_val = quote.get('price')
        print(f"✓ Price: 1 ETH = {price_val:.2f} USDC\n")
    else:
        print(f"✗ Swap estimate failed: {quote.get('error')}\n")
    
    # Test 4: Estimate reverse swap (1000 USDC -> ETH)
    print("Test 4: Estimating swap: 1000 USDC → ETH")
    quote2 = price_client.estimate_swap_output("USDC", "ETH", 1000.0)
    if quote2.get("success"):
        print(f"✓ Input: 1000 USDC")
        print(f"✓ Estimated Output: {quote2['estimated_output']:.6f} ETH")
        price_val = quote2.get('price')
        print(f"✓ Price: 1 ETH = {price_val:.2f} USD\n")
    else:
        print(f"✗ Swap estimate failed: {quote2.get('error')}\n")
    
    print("Tests completed!")

if __name__ == "__main__":
   
    test_prices()