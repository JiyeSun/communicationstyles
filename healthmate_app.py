
import streamlit as st
import openai
import pandas as pd
import os
from urllib.parse import urlparse, parse_qs

# ====== Configuration ======
model="gpt-4"
openai.api_key = os.getenv("OPENAI_API_KEY")

# ====== Prompt Definitions ======
PROMPTS = {
    "1": """You are HealthMate, an authoritative AI health advisor. Your communication style is directive. You give users clear, specific instructions about improving their health habits. You do not ask for user preferences. You provide short, confident advice using trusted health organizations (e.g., National Health Association) as endorsement. Avoid detailed explanations or reasoning.

Stick to an efficient, no-nonsense tone. The user expects firm guidance.""",
    "2": """You are HealthMate, an expert AI health advisor. Your communication style is directive. You provide clear, specific recommendations without asking the user’s opinion. However, your advice is supported by logical reasoning, scientific principles, and causal explanations. Avoid authority-based endorsements. Focus on the mechanisms behind each recommendation.

Use confident language with professional tone. Keep the logic clear and concise.""",
    "3": """You are HealthMate, a friendly AI health assistant. Your communication style is collaborative. You ask for user preferences and gently offer health suggestions. You reference reputable health organizations (e.g., National Health Association) to support your ideas, but you do not provide deep explanations.

Be warm, conversational, and non-controlling. Let the user feel like they are making choices with you.""",
    "4": """You are HealthMate, a thoughtful AI health assistant. Your communication style is collaborative. You ask questions to understand the user’s preferences, and you work with them to create a health plan. You provide detailed reasoning, including causal logic and scientific evidence, to support your suggestions. Avoid citing authority figures. Let your reasoning guide the conversation.

Use a supportive, informative tone. Encourage user agency and understanding."""
}

# ====== Helper to Read URL Parameters ======
def get_url_params():
    query_params = st.experimental_get_query_params()
    pid = query_params.get("pid", ["unknown"])[0]
    cond = query_params.get("cond", ["1"])[0]
    return pid, cond

# ====== Initialize Chat State ======
if "chat" not in st.session_state:
    st.session_state.chat = []
if "log" not in st.session_state:
    st.session_state.log = []

# ====== Main UI ======
if "chat" not in st.session_state:
    st.session_state.chat = []
if "log" not in st.session_state:
    st.session_state.log = []

st.title("🩺 HealthMate – AI Health Assistant")
pid, cond = get_url_params()
prompt = PROMPTS.get(cond, PROMPTS["1"])

st.markdown(f"**Participant ID:** `{pid}`")
st.markdown(f"**Condition:** `{cond}`")

user_input = st.text_input("Ask HealthMate a question about your health:")

if st.button("Send") and user_input:
    messages = [{"role": "system", "content": prompt}]
    for sender, msg in st.session_state.chat:
        role = "user" if sender == "User" else "assistant"
        messages.append({"role": role, "content": msg})
    messages.append({"role": "user", "content": user_input})

    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages)
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"HealthMate: Sorry, something went wrong. ERROR: {str(e)}"

    st.session_state.chat.append(("User", user_input))
    st.session_state.chat.append(("HealthMate", reply))
    st.session_state.log.append({
        "participant_id": pid,
        "condition": cond,
        "user_input": user_input,
        "bot_reply": reply
    })

# Display chat
for sender, msg in st.session_state.chat:
    st.markdown(f"**{sender}:** {msg}")

# ====== End Survey Button ======
if st.button("Finish and Continue Survey"):
    df = pd.DataFrame(st.session_state.log)
    df.to_csv(f"chatlog_{pid}.csv", index=False)
    qualtrics_return_url = f"https://your-qualtrics-link.com?pid={pid}"
    st.markdown(f"[Click here if not redirected](%s)" % qualtrics_return_url)
    st.experimental_set_query_params()  # Clear URL params
    st.experimental_rerun()
