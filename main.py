import streamlit as st
from backend import generateResponse

st.set_page_config(layout="wide", page_title="ChatBot", page_icon="💬")

# ======= Custom CSS =======
st.markdown("""
<style>
body {
    background-color: #f0f2f6;
    font-family: sans-serif;
}

.chat-container {
    max-width: 600px;
    margin: 20px auto;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
    height: 500px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
}

.message {
    padding: 10px 15px;
    border-radius: 20px;
    margin-bottom: 10px;
    max-width: 70%;
    word-wrap: break-word;
    display: inline-block;
}

.user-message {
    background-color: #DCF8C6;
    align-self: flex-end;
    color: #333;
}

.bot-message {
    background-color: #E5E5EA;
    align-self: flex-start;
    color: #333;
}

.input-area {
    max-width: 600px;
    margin: 10px auto;
    display: flex;
}

input[type="text"] {
    flex-grow: 1;
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 20px;
    margin-right: 10px;
}

button {
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
}

.reset-button {
    display: block;
    margin: 20px auto;
    padding: 10px 20px;
    background-color: #f44336;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
}

.chat-title {
    text-align: center;
    margin-bottom: 20px;
    font-weight: bold;
    font-size: 1.5em;
}

.input-area {
    background-color: #f0f0f0;
    padding: 10px 0;
    border-top: 1px solid #ddd;
}
</style>
""", unsafe_allow_html=True)

# ======= Session State =======
if "history" not in st.session_state:
    st.session_state.history = []

# ======= Title =======
st.markdown('<div class="chat-title">💬 Chat with SMW</div>', unsafe_allow_html=True)

# ======= Chat Display =======
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for user_msg, bot_msg in st.session_state.history:
    st.markdown(f'<div class="message user-message">{user_msg}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="message bot-message">{bot_msg}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ======= Input Area =======
st.markdown('<div class="input-area">', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input("", placeholder="Type your message...", key="user_input")

with col2:
    send_clicked = st.button("Send", disabled=not user_input.strip())

st.markdown('</div>', unsafe_allow_html=True)

# ======= JS for Enter Key to Trigger Button and Scroll =======
st.markdown("""
<script>
const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
input.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const btn = window.parent.document.querySelector('button');
        if (btn && !btn.disabled) btn.click();
    }
});

const chatContainer = document.querySelector('.chat-container');
if (chatContainer) {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
</script>
""", unsafe_allow_html=True)

# ======= Handle Send =======
if send_clicked and user_input.strip():
    with st.spinner("SMW is typing..."):
        try:
            response_text = generateResponse(user_input.strip())
        except Exception as e:
            response_text = f"⚠️ Error generating response: {e}"
    st.session_state.history.append((user_input.strip(), response_text))
    st.rerun()

# ======= Reset Button =======
if st.button("Reset Chat", key="reset_button"):
    st.session_state.history = []
    st.rerun()