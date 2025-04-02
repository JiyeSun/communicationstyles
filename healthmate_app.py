
import streamlit as st
import openai
import pandas as pd
import os
from google_sheet_writer import write_to_google_sheet

# ====== Configuration ======
model = "gpt-4"
openai.api_key = os.getenv("OPENAI_API_KEY")

# ====== Prompt Definitions ======
PROMPTS = {
    "1": "You are HealthMate, an authoritative AI health advisor. Your communication style is directive. You give users clear, specific instructions...",
    "2": "You are HealthMate, an expert AI health advisor. Your communication style is directive. You give specific advice with logical reasoning...",
    "3": "You are HealthMate, a friendly AI health advisor. Your communication style is collaborative. You ask preferences and provide suggestions...",
    "4": "You are HealthMate, a thoughtful AI health advisor. Your communication style is collaborative. You explain in detail using scientific logic..."
}

# ====== URL Param Reader ======
def get_url_params():
    query_params = st.query_params
    pid = query_params.get("pid", "unknown")
    cond = query_params.get("cond", "1")
    return pid, cond

# ====== Init State ======
if "chat" not in st.session_state:
    st.session_state.chat = []
if "log" not in st.session_state:
    st.session_state.log = []

# ====== UI ======
st.title("🩺 HealthMate – AI Health Assistant")
pid, cond = get_url_params()
prompt = PROMPTS.get(cond, PROMPTS["1"])

# ====== Debug Info ======
debug = True
if debug:
    st.markdown("### 🛠️ Debug Info")
    st.markdown(f"- **Participant ID**: `{pid}`")
    st.markdown(f"- **Condition**: `{cond}`")
    st.markdown("---")

# ====== Main Interaction ======
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
            messages=messages
        )
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

# Show history
for sender, msg in st.session_state.chat:
    st.markdown(f"**{sender}:** {msg}")

if st.button("Finish and continue survey"):
    df = pd.DataFrame(st.session_state.log)
    df.to_csv(f"chatlog_{pid}.csv", index=False)
    write_to_google_sheet(st.session_state.log)
    redirect_url = f"https://iu.ca1.qualtrics.com/jfe/form/SV_es9wQhWHcJ9lg1M?pid={pid}&cond={cond}"
    html_redirect = (
        f'<meta http-equiv="refresh" content="1;url={redirect_url}">'
        f'<p style="display:none;">Redirecting... <a href=\"{redirect_url}\">Click here</a>.</p>'
    )
    st.markdown(html_redirect, unsafe_allow_html=True)
