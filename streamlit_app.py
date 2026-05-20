import json
import os
import uuid
from datetime import datetime

import requests
import streamlit as st

API_BASE = os.getenv("MIYE_API_BASE", "http://localhost:8000")

st.set_page_config(page_title="Miye Demo", layout="wide")

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I’m Miye. I can help with Base swaps and sends."}
    ]

if "last_transaction" not in st.session_state:
    st.session_state.last_transaction = None

if "last_quote_data" not in st.session_state:
    st.session_state.last_quote_data = None

def call_chat_api(message: str):
    payload = {
        "message": message,
        "conversation_id": st.session_state.conversation_id,
        "user_address": None,
    }
    r = requests.post(f"{API_BASE}/chat", json=payload, timeout=90)
    r.raise_for_status()
    return r.json()

def format_transaction(tx):
    if not tx:
        return "No transaction proposal."
    return json.dumps(tx, indent=2, ensure_ascii=False)

st.title("Miye")
st.caption("Base-only conversational agent for token swaps and sends.")

with st.sidebar:
    st.subheader("Demo controls")
    st.write(f"Conversation ID: `{st.session_state.conversation_id}`")
    if st.button("New conversation"):
        st.session_state.conversation_id = str(uuid.uuid4())
        st.session_state.messages = [
            {"role": "assistant", "content": "New chat started. I’m Miye."}
        ]
        st.session_state.last_transaction = None
        st.session_state.last_quote_data = None
        st.rerun()

    st.subheader("Quick prompts")
    quick_prompts = [
        "Swap 1 ETH to USDC",
        "Send 10 USDC to mum",
        "What can you do?",
        "Swap 2 SOL to USDC",
        "Tell me a joke",
    ]
    for p in quick_prompts:
        if st.button(p, use_container_width=True):
            st.session_state._pending_prompt = p
            st.rerun()

col1, col2 = st.columns([1.15, 0.85], gap="large")

with col1:
    st.subheader("Chat")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    pending = st.session_state.pop("_pending_prompt", None) if "_pending_prompt" in st.session_state else None

    user_input = st.chat_input("Ask Miye to swap or send tokens on Base...")
    message = pending or user_input

    if message:
        st.session_state.messages.append({"role": "user", "content": message})
        with st.chat_message("user"):
            st.write(message)

        with st.chat_message("assistant"):
            with st.spinner("Miye is thinking..."):
                try:
                    data = call_chat_api(message)
                    response_text = data.get("message", "")
                    tx = data.get("proposed_transaction")
                    quote_data = data.get("quote_data")
                    st.session_state.last_transaction = tx
                    st.session_state.last_quote_data = quote_data
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    st.write(response_text)
                except requests.RequestException as e:
                    error_text = f"Backend error: {e}"
                    st.session_state.messages.append({"role": "assistant", "content": error_text})
                    st.error(error_text)

with col2:
    st.subheader("Proposal")
    if st.session_state.last_transaction:
        st.code(format_transaction(st.session_state.last_transaction), language="json")

        confirm_disabled = False
        if st.button("Simulate confirm", type="primary", use_container_width=True, disabled=confirm_disabled):
            tx = st.session_state.last_transaction
            st.success("Transaction confirmed in demo mode.")
            st.json(
                {
                    "status": "success",
                    "transaction_hash": f"demo_{uuid.uuid4().hex[:10]}",
                    "confirmed_at": datetime.utcnow().isoformat() + "Z",
                    "proposal": tx,
                }
            )
    else:
        st.info("No swap/send proposal yet.")

    st.subheader("Raw quote / metadata")
    if st.session_state.last_quote_data:
        st.json(st.session_state.last_quote_data)
    else:
        st.caption("No quote data returned yet.")

st.divider()
st.caption("Demo mode only. No wallet connection. No on-chain signing. No real transaction execution.")