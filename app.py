"""
app.py
The Streamlit chat interface — this is what turns bot.py from a
terminal script into something that looks and feels like a real app.

Streamlit reruns this whole file top-to-bottom every time the user
does something (types a message, etc.), so we use st.session_state
to remember things across those reruns — like the chat history and
who's currently using the bot.
"""

import streamlit as st
from database import init_db
from bot import handle_message

# Make sure the database/table exists before anything else runs.
init_db()

st.set_page_config(page_title="Internship Tracker Bot", page_icon="📋")
st.title("📋 Internship Tracker Bot")
st.caption("Track your internship applications by just chatting.")

# --- Step 1: figure out who's using the bot ---
# We ask for a name once per session so each friend's applications
# stay separate (this matches user_name in the database schema).
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if st.session_state.user_name is None:
    name_input = st.text_input("What's your name? (so I can track your applications separately)")
    if name_input:
        st.session_state.user_name = name_input.strip().lower()
        st.session_state.chat_history = [
            ("bot", f"Hey {name_input.strip()}! I can help you track internship applications. "
                    "Type 'help' anytime to see what I can do.")
        ]
        st.rerun()
    st.stop()  # Don't show the chat until we have a name

# --- Step 2: normal chat interface ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Show a small reminder of who's logged in, with a way to switch users
with st.sidebar:
    st.write(f"Chatting as: **{st.session_state.user_name}**")
    if st.button("Switch user"):
        st.session_state.user_name = None
        st.session_state.chat_history = []
        st.rerun()

# Replay the full conversation so far (Streamlit reruns the script
# on every interaction, so without this the chat would "forget"
# everything shown before the latest message).
for sender, message in st.session_state.chat_history:
    with st.chat_message("user" if sender == "user" else "assistant"):
        st.write(message)

# The actual chat input box at the bottom of the page.
user_message = st.chat_input("Type a message...")

if user_message:
    st.session_state.chat_history.append(("user", user_message))

    bot_reply = handle_message(st.session_state.user_name, user_message)
    st.session_state.chat_history.append(("bot", bot_reply))

    # Rerun so the new messages show up immediately.
    st.rerun()
