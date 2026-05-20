# Miye Agent API Documentation

This documentation is intended for frontend developers integrating the Miye AI Swap Assistant.

## Base URL
Default: `http://localhost:8000`

## Endpoints

### 1. Chat & Transaction Proposal
**Endpoint:** `POST /chat`  
**Description:** The primary entry point for all conversational interactions. Use this to send user messages and receive either a text response or a transaction proposal.

#### Request Body (`ChatRequest`)
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `string` | Yes | The user's natural language input. |
| `conversation_id` | `string` | No | UUID or unique string to maintain chat history. Defaults to `default_user`. |
| `user_address` | `string` | No | The connected wallet address (0x...). Used for address-specific context. |

#### Response Body (`ChatResponse`)
| Field | Type | Description |
| :--- | :--- | :--- |
| `message` | `string` | The agent's conversational text response. |
| `proposed_transaction` | `object` \| `null` | A structured transaction payload if the agent is suggesting a swap/send. |
| `quote_data` | `object` \| `null` | Raw price data from the agent's internal quote tool. |
| `conversation_id` | `string` | The ID of the session used. |

---

### 2. Transaction Proposal Objects
When `proposed_transaction` is returned, it will follow one of two schemas based on the `action` field.

#### A. Swap Proposal (`action: "swap"`)
Returned when the user wants to trade tokens on Base.
```json
{
  "action": "swap",
  "tokenIn": "ETH",
  "tokenInAddress": "0x0000000000000000000000000000000000000000",
  "tokenOut": "USDC",
  "tokenOutAddress": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "amount": "1.0",
  "estimatedOutput": "2450.50",
  "maxSlippage": "0.5",
  "chain": "base",
  "routerAddress": "0x2626664c2603336E57B271c5C0b26F421741e481"
}
```

#### B. Send Proposal (`action: "send"`)
Returned when the user wants to send tokens to another address.
```json
{
  "action": "send",
  "token": "USDC",
  "tokenAddress": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "toAddress": "0xRecipientAddress...",
  "amount": "100.0",
  "chain": "base"
}
```

---

### 3. Conversation Flow & State
The agent is **stateful**. It remembers the last 16 messages in a `conversation_id`.

**Typical Workflow:**
1. **User:** "I want to swap 1 ETH for USDC."
2. **Agent:** Returns a `message` ("I've fetched a quote...") and `proposed_transaction`.
3. **Frontend:** Detects `proposed_transaction`, renders the `SwapCard`.
4. **User:** Clicks "Confirm" in UI, signs in wallet.
5. **Frontend:** Waits for transaction confirmation on-chain.
6. **Frontend (Feedback Loop):** Sends a hidden message to `/chat`:  
   *Message:* `Transaction 0xHash... completed with status success`
7. **Agent:** Responds with a conversational confirmation: "Transaction successful! You can view it on Basescan here..."

---

### 4. Utility Endpoints

#### Health Check
**Endpoint:** `GET /health`  
**Response:** `{"status": "healthy"}`

---

### 5. Error Handling
The API returns standard HTTP status codes:
- `400 Bad Request`: Missing message or invalid parameters.
- `500 Internal Server Error`: Agent execution failure or LLM timeout.
