import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
GEMINI_MODEL = "gemini-2.5-flash-lite"
TEMPERATURE = 0.74
MAX_OUTPUT_TOKENS = 1008
MAX_CONTEXT = 16

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Blockchain Config
# Uniswap Universal Router on Base
UNISWAP_ROUTER_ADDRESS = os.getenv("UNISWAP_ROUTER_ADDRESS", "0x2626664c2603336E57B271c5C0b26F421741e481")
BASE_CHAIN_ID = "base"

