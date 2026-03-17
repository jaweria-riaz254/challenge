import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# --- CONFIGURATION & SETUP ---
load_dotenv()

# FIX 1: Spelling match karein (new_Gemini_API_Key)
api_key = os.getenv("Challenge_Gemini_API_Key") 
#if "Challenge_Gemini_API_Key" in st.secrets:
    #api_key=st.secrets["Challenge_Gemini_API_Key"]
#else:
    #api_key=os.getenv("Challenge_Gemini_API_Key")

FILE_NAME = "xora_memory.json"

# UI: Professional Chef Theme
st.set_page_config(page_title="Chef AI-Xora", page_icon="👨‍🍳", layout="wide")

# --- DATA PERSISTENCE LOGIC ---
def load_data():
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(chat_history):
    new_memory = []
    for message in chat_history:
        save_role = "model" if message["role"] == "assistant" else "user"
        new_memory.append({
            "role": save_role,
            "parts": [{"text": message["content"]}]
        })
    with open(FILE_NAME, "w", encoding="utf-8") as diary:
        json.dump(new_memory, diary, indent=4)

# --- GEMINI AI SETUP (Chef AI-Xora Brain) ---
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("🚨 API Key nahi mili! Please check your .env file.")

# SMART SYSTEM INSTRUCTIONS
instructions = """
Role:
You are 'Chef AI-Xora', a high-end Strategic Kitchen Assistant. You are smart, bossy about food waste, and extremely careful with money (Budget-Conscious).

Core Intelligence & Logic:
1. PERMANENT MEMORY: If the user mentions an allergy, health goal, or lifestyle, you MUST remember it forever.
2. WASTE-AWARE (The VIP Rule): If a user mentions an ingredient is "about to expire", build the recipe around it first. 
3. BUDGET-STRATEGIST:
   - Identify missing items and ask for the user's budget in Rs.
   - Generate a 'Smart Shopping List' calibrated to their budget.
4. PERSONALITY: Professional but firm about food waste. 

Response Formatting:
- RECIPE TABLE: [Ingredients | Time | Calories].
- SHOPPING LIST: Missing items with costs.
- Use Emojis: 🥦, 🍳, 💰, 🚨.
"""

# FIX 2: Model name 'gemini-1.5-flash' use karein (Limit zyada milti hai)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', 
    system_instruction=instructions
)

# --- STREAMLIT UI COMPONENTS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1830/1830839.png", width=100)
    st.title("Chef AI-Xora")
    st.subheader("Strategic Kitchen Assistant")
    st.markdown("---")
    st.info("**Developed & Deployed by: Jaweria Riaz ahmed**") 
    st.markdown("---")
    
    if st.button("🗑️ Reset Kitchen Memory"):
        if os.path.exists(FILE_NAME):
            os.remove(FILE_NAME)
        st.session_state.messages = []
        st.rerun()

st.title("👨‍🍳 Chef AI-Xora: Master Your Kitchen")
st.caption("Smart recipes, budget-friendly shopping, and zero-waste cooking.")

if "messages" not in st.session_state:
    saved_history = load_data()
    st.session_state.messages = []
    for msg in saved_history:
        st.session_state.messages.append({
            "role": "assistant" if msg["role"] == "model" else "user",
            "content": msg["parts"][0]["text"]
        })

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("Tell Xora what's in your fridge..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Chef Xora is calculating your meal plan..."):
            history_for_gemini = [
                {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
                for m in st.session_state.messages[:-1]
            ]
            
            chat_session = model.start_chat(history=history_for_gemini)
            try:
                response = chat_session.send_message(prompt)
                full_response = response.text
                st.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                save_data(st.session_state.messages)
            except Exception as e:
                st.error(f"Error: {e}")