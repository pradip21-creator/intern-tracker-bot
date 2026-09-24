"""
database.py
Handles the SQLite database setup for the Internship Tracker Bot.

Each row = one internship application, tied to a user_name so
multiple friends can share the same database without mixing data.
"""

import sqlite3

DB_NAME = "tracker.db"


def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)


def init_db():
    """Create the applications table if it doesn't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            company TEXT NOT NULL,
            role TEXT,
            deadline DATE,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized: tracker.db (table 'applications' ready)")


if __name__ == "__main__":
    init_db()
