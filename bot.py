"""
bot.py
Ties intent_matcher.py (understanding) + crud.py (doing) together.

The tricky part: a message like "add a new application" tells us
WHAT to do, but not the actual details (company, role, deadline).
So for multi-step actions, the bot needs to remember "I'm in the
middle of adding something for this user" and ask follow-up
questions — this is called CONVERSATION STATE.

We track one pending "step" per user in a dictionary. In a real
production app this would live in a database or session store;
for a college project, an in-memory dict is a reasonable and
explainable choice (with the trade-off noted below).
"""

from database import init_db
from crud import add_application, list_applications, get_upcoming, update_status, delete_application
from intent_matcher import detect_intent

# Tracks what each user is in the middle of doing.
# Example: {"pradip": {"action": "add", "step": "company", "data": {}}}
# Trade-off: this resets if the program restarts, since it's just
# a Python dictionary in memory, not saved to the database.
_pending_actions = {}


def _format_application_row(row):
    """Turn a raw database row into a readable line."""
    app_id, company, role, deadline, status = row
    role_part = f" ({role})" if role else ""
    return f"[{app_id}] {company}{role_part} — due {deadline} — {status}"


def handle_message(user_name, text):
    """
    Main entry point: given what a user typed, return the bot's reply.
    Handles both fresh requests AND continuing a multi-step action.
    """

    # --- Case 1: user is in the middle of a multi-step action ---
    if user_name in _pending_actions:
        return _continue_pending_action(user_name, text)

    # --- Case 2: fresh message, figure out the intent ---
    intent, confidence = detect_intent(text)

    if intent == "add":
        _pending_actions[user_name] = {"action": "add", "step": "company", "data": {}}
        return "Sure! What's the company name?"

    elif intent == "list_all":
        rows = list_applications(user_name)
        if not rows:
            return "You don't have any applications tracked yet. Want to add one?"
        return "Here's everything you've got:\n" + "\n".join(_format_application_row(r) for r in rows)

    elif intent == "list_pending":
        rows = list_applications(user_name, status="pending")
        if not rows:
            return "Nothing pending right now."
        return "Pending applications:\n" + "\n".join(_format_application_row(r) for r in rows)

    elif intent == "upcoming":
        rows = get_upcoming(user_name, days=7)
        if not rows:
            return "Nothing due in the next 7 days."
        return "Coming up in the next 7 days:\n" + "\n".join(_format_application_row(r) for r in rows)

    elif intent == "update_status":
        _pending_actions[user_name] = {"action": "update_status", "step": "id", "data": {}}
        return "Which application id do you want to update? (use 'list' to check ids)"

    elif intent == "delete":
        _pending_actions[user_name] = {"action": "delete", "step": "id", "data": {}}
        return "Which application id do you want to delete?"

    elif intent == "help":
        return (
            "I can help you track internship applications. Try things like:\n"
            "- 'add a new application'\n"
            "- 'show all my applications'\n"
            "- 'what's due soon'\n"
            "- 'update the status'\n"
            "- 'delete an application'"
        )

    else:
        return "I didn't quite get that. Type 'help' to see what I can do."


def _continue_pending_action(user_name, text):
    """Handle the next step of a multi-turn action already in progress."""
    pending = _pending_actions[user_name]
    action = pending["action"]
    step = pending["step"]
    data = pending["data"]

    if action == "add":
        if step == "company":
            data["company"] = text.strip()
            pending["step"] = "role"
            return "Got it. What's the role/position? (or type 'skip')"

        elif step == "role":
            data["role"] = None if text.strip().lower() == "skip" else text.strip()
            pending["step"] = "deadline"
            return "What's the deadline? (format: YYYY-MM-DD)"

        elif step == "deadline":
            data["deadline"] = text.strip()
            new_id = add_application(user_name, data["company"], data["role"], data["deadline"])
            del _pending_actions[user_name]
            return f"Added! '{data['company']}' is tracked with id {new_id}."

    elif action == "update_status":
        if step == "id":
            data["id"] = text.strip()
            pending["step"] = "status"
            return "What's the new status? (pending / applied / interview / rejected / accepted)"

        elif step == "status":
            success = update_status(data["id"], text.strip().lower())
            del _pending_actions[user_name]
            if success:
                return f"Updated application {data['id']} to '{text.strip().lower()}'."
            return f"Couldn't find an application with id {data['id']}."

    elif action == "delete":
        if step == "id":
            success = delete_application(text.strip())
            del _pending_actions[user_name]
            if success:
                return f"Deleted application {text.strip()}."
            return f"Couldn't find an application with id {text.strip()}."

    # Fallback safety net — shouldn't normally reach here
    del _pending_actions[user_name]
    return "Something went wrong with that action, let's start over."


if __name__ == "__main__":
    # Quick manual conversation simulation to prove multi-turn works
    init_db()

    conversation = [
        "hi, add a new application",
        "Microsoft",
        "SWE Intern",
        "2026-11-15",
        "show all my applications",
        "what's due soon",
    ]

    print("--- Simulated conversation for user 'testuser' ---")
    for msg in conversation:
        reply = handle_message("testuser", msg)
        print(f"User: {msg}")
        print(f"Bot: {reply}\n")
