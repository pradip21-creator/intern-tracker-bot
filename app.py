"""
app.py
The Streamlit chat interface, now with real login/register instead
of just typing a name — so each person's data is actually private.
"""

import streamlit as st
from database import init_db
from auth import register_user, verify_login
from bot import handle_message

init_db()

st.set_page_config(page_title="Internship Tracker Bot", page_icon="📋")
st.title("📋 Internship Tracker Bot")
st.caption("Track your internship applications by just chatting.")

# --- Step 1: login / register screen ---
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if st.session_state.logged_in_user is None:
    tab_login, tab_register = st.tabs(["Log in", "Create account"])

    with tab_login:
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log in"):
            success, message = verify_login(login_username, login_password)
            if success:
                st.session_state.logged_in_user = login_username.strip().lower()
                st.session_state.chat_history = [
                    ("bot", f"Welcome back, {login_username.strip()}! Type 'help' to see what I can do.")
                ]
                st.rerun()
            else:
                st.error(message)

    with tab_register:
        new_username = st.text_input("Choose a username", key="reg_username")
        new_password = st.text_input("Choose a password", type="password", key="reg_password")
        if st.button("Create account"):
            success, message = register_user(new_username, new_password)
            if success:
                st.success(message + " You can now log in from the 'Log in' tab.")
            else:
                st.error(message)

    st.stop()  # Don't show the chat until logged in

# --- Step 2: normal chat interface (only reachable when logged in) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.write(f"Logged in as: **{st.session_state.logged_in_user}**")
    if st.button("Log out"):
        st.session_state.logged_in_user = None
        st.session_state.chat_history = []
        st.rerun()

for sender, message in st.session_state.chat_history:
    with st.chat_message("user" if sender == "user" else "assistant"):
        st.write(message)

user_message = st.chat_input("Type a message...")

if user_message:
    st.session_state.chat_history.append(("user", user_message))

    bot_reply = handle_message(st.session_state.logged_in_user, user_message)
    st.session_state.chat_history.append(("bot", bot_reply))

    st.rerun()
