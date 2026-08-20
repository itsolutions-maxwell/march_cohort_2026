"""
Seeds a small set of physical rooms into every hospital dataset, so staff
have something to assign right after setup. Safe to re-run — it checks for
an existing room_number before inserting.

Usage (from the hospital-analytics/ directory, after setup_bigquery.py):

    python -m bigquery.seed_rooms
"""

import uuid

from app.bigquery_client import insert_room, room_number_exists
from app.config import HOSPITALS

# (room_number, room_type, floor)
DEMO_ROOMS = [
    ("101", "general", 1),
    ("102", "general", 1),
    ("103", "private", 1),
    ("104", "semi_private", 1),
    ("201", "icu", 2),
    ("202", "icu", 2),
    ("203", "er", 2),
    ("204", "operating_room", 2),
]


def seed_room(hospital: str, room_number: str, room_type: str, floor: int) -> None:
    if room_number_exists(hospital, room_number):
        print(f"  Already exists: room {room_number} in {hospital}")
        return

    insert_room(hospital, room_id=str(uuid.uuid4()), room_number=room_number, room_type=room_type, floor=floor)
    print(f"  Seeded: room {room_number} ({room_type}, floor {floor}) in {hospital}")


def main() -> None:
    for hospital, name in HOSPITALS.items():
        print(f"{name} ({hospital}):")
        for room_number, room_type, floor in DEMO_ROOMS:
            seed_room(hospital, room_number, room_type, floor)


if __name__ == "__main__":
    main()
