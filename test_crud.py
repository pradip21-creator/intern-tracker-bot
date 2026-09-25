"""
test_crud.py
Quick manual test to confirm the CRUD functions work as expected.
Not a formal test suite — just enough to sanity-check Day 2 before pushing.
Run this, read the output, then delete tracker.db if you want a clean slate.
"""

from database import init_db
from crud import add_application, list_applications, get_upcoming, update_status, delete_application

init_db()

print("\n--- Adding applications ---")
id1 = add_application("pradip", "Google", "SWE Intern", "2026-10-01")
id2 = add_application("pradip", "Infosys", "AI Intern", "2026-09-28")
id3 = add_application("riya", "TCS", "Backend Intern", "2026-12-01")
print(f"Added application ids: {id1}, {id2}, {id3}")

print("\n--- Listing pradip's applications ---")
for row in list_applications("pradip"):
    print(row)

print("\n--- pradip's upcoming (next 30 days) ---")
for row in get_upcoming("pradip", days=30):
    print(row)

print("\n--- Updating status of id1 to 'interview' ---")
update_status(id1, "interview")
for row in list_applications("pradip"):
    print(row)

print("\n--- Deleting id2 ---")
delete_application(id2)
for row in list_applications("pradip"):
    print(row)

print("\n--- riya's applications (should be untouched, only 1 row) ---")
for row in list_applications("riya"):
    print(row)
