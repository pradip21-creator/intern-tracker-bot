"""
auth.py
Real user accounts: register + login, so each person's data is
actually private, not just separated by typing a different name.

IMPORTANT SECURITY NOTE (good to mention if your teacher asks):
We hash passwords with SHA-256 + a per-user random salt before
storing them. We NEVER store the plain password itself. A hash
is one-way — you can check "does this password match?" but you
can't reverse a hash back into the original password.

For a real production app, you'd use a slower, purpose-built
algorithm like bcrypt or argon2 (SHA-256 is fast, which actually
makes it weaker against attackers guessing many passwords). SHA-256
+ salt is a reasonable, explainable choice for a college project
that still avoids the #1 mistake: storing plain-text passwords.
"""

import hashlib
import secrets
from database import get_connection


def _hash_password(password, salt):
    """Combine password + salt, then hash. Same input always gives same output."""
    combined = (password + salt).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


def register_user(username, password):
    """
    Create a new account. Returns (success: bool, message: str).
    Fails if the username is already taken.
    """
    username = username.strip().lower()

    if not username or not password:
        return False, "Username and password can't be empty."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "That username is already taken."

    salt = secrets.token_hex(16)  # random per-user salt, so identical
                                   # passwords still produce different hashes
    password_hash = _hash_password(password, salt)
    # Store salt alongside the hash (separated by $) so we can verify later.
    stored_value = f"{salt}${password_hash}"

    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, stored_value)
    )
    conn.commit()
    conn.close()
    return True, "Account created!"


def verify_login(username, password):
    """Check username/password. Returns (success: bool, message: str)."""
    username = username.strip().lower()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, "No account with that username."

    stored_value = row[0]
    salt, correct_hash = stored_value.split("$")
    attempt_hash = _hash_password(password, salt)

    if attempt_hash == correct_hash:
        return True, "Login successful."
    return False, "Incorrect password."


if __name__ == "__main__":
    from database import init_db
    init_db()

    print("--- Testing registration ---")
    print(register_user("pradip", "mypassword123"))
    print(register_user("pradip", "anotherpass"))  # should fail, duplicate

    print("\n--- Testing login ---")
    print(verify_login("pradip", "mypassword123"))  # should succeed
    print(verify_login("pradip", "wrongpassword"))   # should fail
    print(verify_login("nobody", "whatever"))         # should fail, no account
