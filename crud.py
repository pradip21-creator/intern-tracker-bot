"""
crud.py
Core database operations for the Internship Tracker Bot.

CRUD = Create, Read, Update, Delete — the four basic operations
any app needs to manage data. This file wraps SQL commands into
simple Python functions so the bot logic (Day 4) doesn't need to
write raw SQL itself.
"""

from database import get_connection


def add_application(user_name, company, role, deadline):
    """Add a new internship application. Returns the new row's id."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO applications (user_name, company, role, deadline)
        VALUES (?, ?, ?, ?)
    """, (user_name, company, role, deadline))

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def list_applications(user_name, status=None):
    """
    List all applications for a user.
    If status is given (e.g. 'pending'), only return those.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute("""
            SELECT id, company, role, deadline, status
            FROM applications
            WHERE user_name = ? AND status = ?
            ORDER BY deadline ASC
        """, (user_name, status))
    else:
        cursor.execute("""
            SELECT id, company, role, deadline, status
            FROM applications
            WHERE user_name = ?
            ORDER BY deadline ASC
        """, (user_name,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_upcoming(user_name, days=7):
    """Get applications with deadlines in the next N days."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, company, role, deadline, status
        FROM applications
        WHERE user_name = ?
          AND deadline BETWEEN date('now') AND date('now', ? || ' days')
        ORDER BY deadline ASC
    """, (user_name, days))

    rows = cursor.fetchall()
    conn.close()
    return rows


def update_status(app_id, new_status):
    """Update the status of an application (e.g. 'applied', 'interview', 'rejected')."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE applications
        SET status = ?
        WHERE id = ?
    """, (new_status, app_id))

    conn.commit()
    rows_changed = cursor.rowcount
    conn.close()
    return rows_changed > 0


def delete_application(app_id):
    """Delete an application by its id."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))

    conn.commit()
    rows_changed = cursor.rowcount
    conn.close()
    return rows_changed > 0
