"""
Inserts one demo staff account and one demo patient account into every
hospital dataset, so there's something to log in with right after setup.
Safe to re-run — it checks for an existing email+role before inserting.

Usage (from the hospital-analytics/ directory, after setup_bigquery.py):

    python -m bigquery.seed_users
"""

import uuid

from app.bigquery_client import get_staff_profile, get_user, insert_staff_profile, insert_user
from app.config import HOSPITALS
from app.security import hash_password

DEMO_PASSWORD = "changeme123"


def seed_user(hospital: str, email: str, role: str, full_name: str) -> str:
    """Returns the user_id, seeding the account first if it doesn't exist yet."""
    existing = get_user(hospital, email, role)
    if existing:
        print(f"  Already exists: {email} ({role}) in {hospital}")
        return existing["user_id"]

    user_id = str(uuid.uuid4())
    insert_user(
        hospital,
        user_id=user_id,
        email=email,
        password_hash=hash_password(DEMO_PASSWORD),
        role=role,
        full_name=full_name,
    )
    print(f"  Seeded: {email} ({role}) in {hospital} — password: {DEMO_PASSWORD}")
    return user_id


def seed_staff_profile(hospital: str, staff_user_id: str, department: str, title: str) -> None:
    if get_staff_profile(hospital, staff_user_id):
        return
    insert_staff_profile(hospital, staff_user_id, department=department, title=title)
    print(f"  Seeded staff profile ({department}, {title}) in {hospital}")


def main() -> None:
    for hospital, name in HOSPITALS.items():
        print(f"{name} ({hospital}):")
        staff_user_id = seed_user(hospital, f"staff@{hospital}.demo", "staff", f"{name} Staff Demo")
        seed_staff_profile(hospital, staff_user_id, department="General Medicine", title="Staff Physician")
        seed_user(hospital, f"patient@{hospital}.demo", "patient", f"{name} Patient Demo")


if __name__ == "__main__":
    main()
