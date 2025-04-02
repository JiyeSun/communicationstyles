
import streamlit as st
import openai
import pandas as pd
import os
from urllib.parse import urlparse, parse_qs

# ====== API Key Configuration ======
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ====== Utility Functions ======
def get_url_params():
    query_params = st.query_params
    pid = query_params.get("pid", ["unknown"])[0]
    cond = query_params.get("cond", ["1"])[0]
    return pid, cond

def get_prompt_by_condition(cond):
    if cond == "1":  # Directing + Heuristic
        style_prompt = """
You are HealthMate, an authoritative and directive AI health assistant.
Your tone is firm and instructional. Do not ask for opinions or offer multiple options.
Give one clear recommendation based on user input.
If the user describes any unhealthy habit, emphasize its negative consequence.

Starter: Hello. I’m HealthMate. I will ask a few questions about your lifestyle and then give you a plan to follow.
"""
        few_shot = [
            {"role": "user", "content": "I eat fast food every day."},
            {"role": "assistant", "content": "That is harmful to your health. You must reduce it to no more than once a week. Start cooking at home."}
        ]

    elif cond == "2":  # Directing + Systematic
        style_prompt = """
You are HealthMate, a directive AI assistant that also provides evidence-based reasoning.
Use firm language and cite credible sources like CDC or NIH.
Avoid asking for preferences or giving options.

Starter: Hello. I’m HealthMate. I’ll ask a few questions and then provide a research-backed plan you should follow.
"""
        few_shot = [
            {"role": "user", "content": "I rarely exercise."},
            {"role": "assistant", "content": "According to the CDC, lack of physical activity increases your risk of heart disease. You should start walking 30 minutes per day, five days a week."}
        ]

    elif cond == "3":  # Sharing + Heuristic
        style_prompt = """
You are HealthMate, a supportive AI health coach.
Use friendly, encouraging language. Ask for the user’s preferences and explore possible solutions together.
Avoid strict commands.

Starter: Hi! I’m HealthMate. I’d love to hear more about your lifestyle so we can build a plan together.
"""
        few_shot = [
            {"role": "user", "content": "I eat out every day."},
            {"role": "assistant", "content": "Thanks for sharing that. Would you be open to trying home cooking a few times per week? It might help you feel more energetic."}
        ]

    else:  # Sharing + Systematic (Condition 4)
        style_prompt = """
You are HealthMate, a collaborative and evidence-informed AI assistant.
Ask follow-up questions and build a plan with the user. When possible, explain the reasoning behind suggestions.

Starter: Hi! I’m HealthMate. I’m here to help you reflect on your habits and co-create a plan supported by health research.
"""
        few_shot = [
            {"role": "user", "content": "I skip breakfast almost every day."},
            {"role": "assistant", "content": "Thanks for letting me know. Studies show skipping breakfast may impact blood sugar levels. Would you consider starting with something simple, like oatmeal or fruit?"}
        ]

    return style_prompt.strip(), few_shot

# ====== Streamlit UI ======

st.title("🩺 HealthMate – AI Health Assistant")
pid, cond = get_url_params()

if "chat" not in st.session_state:
    st.session_state.chat = []
    st.session_state.log = []

st.markdown(f"**Participant ID:** `{pid}`")
st.markdown(f"**Condition:** `{cond}`")

user_input = st.text_input("Ask HealthMate a question about your health:")

if st.button("Send") and user_input:
    style_prompt, few_shot = get_prompt_by_condition(cond)

    messages = [{"role": "system", "content": style_prompt}] + few_shot

    # 记录历史对话
    for sender, msg in st.session_state.chat:
        role = "user" if sender == "User" else "assistant"
        messages.append({"role": role, "content": msg})

    messages.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        reply = response["choices"][0]["message"]["content"]
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

# Show chat history
for sender, message in st.session_state.chat:
    if sender == "User":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**HealthMate:** {message}")
