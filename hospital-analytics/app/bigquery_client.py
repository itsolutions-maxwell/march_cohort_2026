import uuid
from datetime import datetime, timezone
from functools import lru_cache

from google.cloud import bigquery

from app.config import ADMISSION_FEES, ROOM_ASSIGNMENT_FEE, TREATMENT_FEE, settings

USERS_TABLE = "users"
PATIENTS_TABLE = "patients"
STAFF_PROFILES_TABLE = "staff_profiles"
HOSPITAL_INFO_TABLE = "hospital_info"
ROOMS_TABLE = "rooms"
ENCOUNTERS_TABLE = "encounters"
ROOM_ASSIGNMENTS_TABLE = "room_assignments"
TREATMENTS_TABLE = "treatments"
TEST_COMPLETIONS_TABLE = "test_completions"
DISCHARGES_TABLE = "discharges"
BILLING_CHARGES_TABLE = "billing_charges"
PAYMENTS_TABLE = "payments"


@lru_cache
def get_client() -> bigquery.Client:
    return bigquery.Client(project=settings.gcp_project_id)


def _table_ref(hospital: str, table: str) -> str:
    return f"{settings.gcp_project_id}.{hospital}.{table}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# BigQuery projects without billing enabled reject both the streaming
# insert API ("Streaming insert is not allowed in the free tier") and DML
# INSERT/UPDATE ("DML queries are not allowed in the free tier"). A load
# job is the one write path that's free-tier-safe, so all writes go
# through load_table_from_json against the table's existing schema, and
# nothing is ever mutated in place — every state change is its own new
# row, and "current state" is derived at query time from the latest one.
def _load_insert(table: str, row: dict) -> None:
    client = get_client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    client.load_table_from_json([row], table, job_config=job_config).result()


# ---- users / auth ----------------------------------------------------

def get_user(hospital: str, email: str, role: str) -> dict | None:
    client = get_client()
    query = f"""
        SELECT user_id, email, password_hash, role, full_name
        FROM `{_table_ref(hospital, USERS_TABLE)}`
        WHERE email = @email AND role = @role
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email),
            bigquery.ScalarQueryParameter("role", "STRING", role),
        ]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return dict(rows[0]) if rows else None


def email_exists_in_hospital(hospital: str, email: str) -> bool:
    client = get_client()
    query = f"""
        SELECT 1
        FROM `{_table_ref(hospital, USERS_TABLE)}`
        WHERE email = @email
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", email)]
    )
    return len(list(client.query(query, job_config=job_config).result())) > 0


def list_patients(hospital: str) -> list[dict]:
    client = get_client()
    query = f"""
        SELECT user_id, email, full_name
        FROM `{_table_ref(hospital, USERS_TABLE)}`
        WHERE role = 'patient'
        ORDER BY full_name
    """
    return [dict(row) for row in client.query(query).result()]


def get_patient_by_id(hospital: str, user_id: str) -> dict | None:
    client = get_client()
    query = f"""
        SELECT user_id, email, full_name
        FROM `{_table_ref(hospital, USERS_TABLE)}`
        WHERE user_id = @user_id AND role = 'patient'
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return dict(rows[0]) if rows else None


def insert_user(hospital: str, user_id: str, email: str, password_hash: str, role: str, full_name: str) -> None:
    row = {
        "user_id": user_id,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "full_name": full_name,
        "created_at": _now(),
    }
    _load_insert(_table_ref(hospital, USERS_TABLE), row)


# ---- patient demographics ---------------------------------------------

def insert_patient_profile(
    hospital: str,
    patient_user_id: str,
    date_of_birth: str,
    gender: str,
    phone: str,
    blood_type: str,
    payer_type: str,
) -> None:
    row = {
        "patient_user_id": patient_user_id,
        "date_of_birth": date_of_birth,
        "gender": gender,
        "phone": phone,
        "blood_type": blood_type,
        "payer_type": payer_type,
        "created_at": _now(),
    }
    _load_insert(_table_ref(hospital, PATIENTS_TABLE), row)


def get_patient_profile(hospital: str, patient_user_id: str) -> dict | None:
    client = get_client()
    query = f"""
        SELECT patient_user_id, date_of_birth, gender, phone, blood_type, payer_type
        FROM `{_table_ref(hospital, PATIENTS_TABLE)}`
        WHERE patient_user_id = @patient_user_id
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("patient_user_id", "STRING", patient_user_id)]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return dict(rows[0]) if rows else None


# ---- staff profiles ----------------------------------------------------

def insert_staff_profile(hospital: str, staff_user_id: str, department: str, title: str) -> None:
    row = {
        "staff_user_id": staff_user_id,
        "department": department,
        "title": title,
        "created_at": _now(),
    }
    _load_insert(_table_ref(hospital, STAFF_PROFILES_TABLE), row)


def get_staff_profile(hospital: str, staff_user_id: str) -> dict | None:
    client = get_client()
    query = f"""
        SELECT staff_user_id, department, title
        FROM `{_table_ref(hospital, STAFF_PROFILES_TABLE)}`
        WHERE staff_user_id = @staff_user_id
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("staff_user_id", "STRING", staff_user_id)]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return dict(rows[0]) if rows else None


# ---- hospital info -------------------------------------------------------

def insert_hospital_info(hospital: str, hospital_id: str, name: str, address: str, phone: str) -> None:
    row = {
        "hospital_id": hospital_id,
        "name": name,
        "address": address,
        "phone": phone,
        "created_at": _now(),
    }
    _load_insert(_table_ref(hospital, HOSPITAL_INFO_TABLE), row)


def hospital_info_exists(hospital: str) -> bool:
    client = get_client()
    query = f"SELECT 1 FROM `{_table_ref(hospital, HOSPITAL_INFO_TABLE)}` LIMIT 1"
    return len(list(client.query(query).result())) > 0


def get_hospital_info(hospital: str) -> dict | None:
    client = get_client()
    query = f"""
        SELECT hospital_id, name, address, phone
        FROM `{_table_ref(hospital, HOSPITAL_INFO_TABLE)}`
        LIMIT 1
    """
    rows = list(client.query(query).result())
    return dict(rows[0]) if rows else None


# ---- rooms --------------------------------------------------------------

def list_rooms(hospital: str) -> list[dict]:
    client = get_client()
    query = f"""
        SELECT room_id, room_number, room_type, floor
        FROM `{_table_ref(hospital, ROOMS_TABLE)}`
        ORDER BY room_number
    """
    return [dict(row) for row in client.query(query).result()]


def insert_room(hospital: str, room_id: str, room_number: str, room_type: str, floor: int) -> None:
    row = {
        "room_id": room_id,
        "room_number": room_number,
        "room_type": room_type,
        "floor": floor,
        "created_at": _now(),
    }
    _load_insert(_table_ref(hospital, ROOMS_TABLE), row)


def room_number_exists(hospital: str, room_number: str) -> bool:
    client = get_client()
    query = f"""
        SELECT 1 FROM `{_table_ref(hospital, ROOMS_TABLE)}` WHERE room_number = @room_number LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("room_number", "STRING", room_number)]
    )
    return len(list(client.query(query, job_config=job_config).result())) > 0


def get_room_by_id(hospital: str, room_id: str) -> dict | None:
    client = get_client()
    query = f"""
        SELECT room_id, room_number, room_type, floor
        FROM `{_table_ref(hospital, ROOMS_TABLE)}`
        WHERE room_id = @room_id
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("room_id", "STRING", room_id)]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return dict(rows[0]) if rows else None


def list_available_rooms(hospital: str) -> list[dict]:
    """Rooms that aren't the current room of any still-active (non-discharged) encounter."""
    client = get_client()
    query = f"""
        WITH latest_room AS (
            SELECT encounter_id, room_id,
                   ROW_NUMBER() OVER (PARTITION BY encounter_id ORDER BY assigned_at DESC) AS rn
            FROM `{_table_ref(hospital, ROOM_ASSIGNMENTS_TABLE)}`
        ),
        occupied_room_ids AS (
            SELECT lr.room_id
            FROM latest_room lr
            WHERE lr.rn = 1
              AND lr.encounter_id NOT IN (SELECT encounter_id FROM `{_table_ref(hospital, DISCHARGES_TABLE)}`)
        )
        SELECT room_id, room_number, room_type, floor
        FROM `{_table_ref(hospital, ROOMS_TABLE)}`
        WHERE room_id NOT IN (SELECT room_id FROM occupied_room_ids)
        ORDER BY room_number
    """
    return [dict(row) for row in client.query(query).result()]


def get_current_room(hospital: str, encounter_id: str) -> dict | None:
    client = get_client()
    query = f"""
        SELECT r.room_id, r.room_number, r.room_type, r.floor, ra.assigned_at
        FROM `{_table_ref(hospital, ROOM_ASSIGNMENTS_TABLE)}` ra
        JOIN `{_table_ref(hospital, ROOMS_TABLE)}` r ON r.room_id = ra.room_id
        WHERE ra.encounter_id = @encounter_id
        QUALIFY ROW_NUMBER() OVER (ORDER BY ra.assigned_at DESC) = 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("encounter_id", "STRING", encounter_id)]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return dict(rows[0]) if rows else None


def assign_room(hospital: str, encounter_id: str, room_id: str, staff_user_id: str, patient_user_id: str) -> None:
    row = {
        "assignment_id": str(uuid.uuid4()),
        "encounter_id": encounter_id,
        "room_id": room_id,
        "staff_user_id": staff_user_id,
        "assigned_at": _now(),
    }
    _load_insert(_table_ref(hospital, ROOM_ASSIGNMENTS_TABLE), row)
    add_charge(hospital, encounter_id, patient_user_id, "room", "Room assignment fee", ROOM_ASSIGNMENT_FEE)


# ---- encounters -----------------------------------------------------------

def create_encounter(
    hospital: str,
    patient_user_id: str,
    attending_staff_user_id: str,
    encounter_type: str,
    reason: str,
    department: str,
    expected_discharge_date: str | None,
) -> str:
    encounter_id = str(uuid.uuid4())
    row = {
        "encounter_id": encounter_id,
        "patient_user_id": patient_user_id,
        "attending_staff_user_id": attending_staff_user_id,
        "encounter_type": encounter_type,
        "reason": reason,
        "department": department,
        "expected_discharge_date": expected_discharge_date,
        "created_at": _now(),
    }
    _load_insert(_table_ref(hospital, ENCOUNTERS_TABLE), row)
    add_charge(
        hospital,
        encounter_id,
        patient_user_id,
        "admission",
        f"{encounter_type.capitalize()} admission fee",
        ADMISSION_FEES[encounter_type],
    )
    return encounter_id


def _encounter_rows(
    hospital: str,
    where_clause: str = "",
    query_parameters: list | None = None,
    limit: int | None = None,
) -> list[dict]:
    client = get_client()
    params = list(query_parameters or [])
    limit_clause = ""
    if limit:
        limit_clause = "LIMIT @limit"
        params.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))

    query = f"""
        WITH latest_room AS (
            SELECT encounter_id, room_id,
                   ROW_NUMBER() OVER (PARTITION BY encounter_id ORDER BY assigned_at DESC) AS rn
            FROM `{_table_ref(hospital, ROOM_ASSIGNMENTS_TABLE)}`
        )
        SELECT
            e.encounter_id, e.patient_user_id, e.attending_staff_user_id,
            e.encounter_type, e.reason, e.created_at,
            e.department, e.expected_discharge_date,
            p.full_name AS patient_name,
            s.full_name AS staff_name,
            r.room_number, r.room_type,
            d.discharged_at, d.discharge_notes
        FROM `{_table_ref(hospital, ENCOUNTERS_TABLE)}` e
        LEFT JOIN `{_table_ref(hospital, USERS_TABLE)}` p ON p.user_id = e.patient_user_id
        LEFT JOIN `{_table_ref(hospital, USERS_TABLE)}` s ON s.user_id = e.attending_staff_user_id
        LEFT JOIN latest_room lr ON lr.encounter_id = e.encounter_id AND lr.rn = 1
        LEFT JOIN `{_table_ref(hospital, ROOMS_TABLE)}` r ON r.room_id = lr.room_id
        LEFT JOIN `{_table_ref(hospital, DISCHARGES_TABLE)}` d ON d.encounter_id = e.encounter_id
        {where_clause}
        ORDER BY e.created_at DESC
        {limit_clause}
    """
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    rows = [dict(row) for row in client.query(query, job_config=job_config).result()]
    for row in rows:
        row["is_discharged"] = row["discharged_at"] is not None
    return rows


def get_encounter(hospital: str, encounter_id: str) -> dict | None:
    rows = _encounter_rows(
        hospital,
        where_clause="WHERE e.encounter_id = @encounter_id",
        query_parameters=[bigquery.ScalarQueryParameter("encounter_id", "STRING", encounter_id)],
    )
    return rows[0] if rows else None


def list_recent_encounters(hospital: str, limit: int = 50) -> list[dict]:
    return _encounter_rows(hospital, limit=limit)


def list_encounters_for_patient(hospital: str, patient_user_id: str) -> list[dict]:
    return _encounter_rows(
        hospital,
        where_clause="WHERE e.patient_user_id = @patient_user_id",
        query_parameters=[bigquery.ScalarQueryParameter("patient_user_id", "STRING", patient_user_id)],
    )


# ---- treatments -----------------------------------------------------------

def add_treatment(
    hospital: str,
    encounter_id: str,
    staff_user_id: str,
    treatment_type: str,
    notes: str,
    patient_user_id: str,
    category: str,
) -> None:
    row = {
        "treatment_id": str(uuid.uuid4()),
        "encounter_id": encounter_id,
        "staff_user_id": staff_user_id,
        "treatment_type": treatment_type,
        "category": category,
        "notes": notes,
        "administered_at": _now(),
    }
    _load_insert(_table_ref(hospital, TREATMENTS_TABLE), row)
    add_charge(hospital, encounter_id, patient_user_id, "treatment", treatment_type, TREATMENT_FEE)


def list_treatments_for_encounter(hospital: str, encounter_id: str) -> list[dict]:
    client = get_client()
    query = f"""
        SELECT
            t.treatment_id, t.treatment_type, t.category, t.notes, t.administered_at,
            s.full_name AS staff_name,
            c.completed_at, c.result_notes
        FROM `{_table_ref(hospital, TREATMENTS_TABLE)}` t
        LEFT JOIN `{_table_ref(hospital, USERS_TABLE)}` s ON s.user_id = t.staff_user_id
        LEFT JOIN `{_table_ref(hospital, TEST_COMPLETIONS_TABLE)}` c ON c.treatment_id = t.treatment_id
        WHERE t.encounter_id = @encounter_id
        ORDER BY t.administered_at DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("encounter_id", "STRING", encounter_id)]
    )
    rows = [dict(row) for row in client.query(query, job_config=job_config).result()]
    for row in rows:
        row["is_pending"] = row["completed_at"] is None
    return rows


def complete_test(hospital: str, treatment_id: str, staff_user_id: str, result_notes: str) -> None:
    row = {
        "test_completion_id": str(uuid.uuid4()),
        "treatment_id": treatment_id,
        "staff_user_id": staff_user_id,
        "result_notes": result_notes,
        "completed_at": _now(),
    }
    _load_insert(_table_ref(hospital, TEST_COMPLETIONS_TABLE), row)


# ---- discharges -----------------------------------------------------------

def discharge_encounter(hospital: str, encounter_id: str, staff_user_id: str, discharge_notes: str) -> None:
    row = {
        "discharge_id": str(uuid.uuid4()),
        "encounter_id": encounter_id,
        "staff_user_id": staff_user_id,
        "discharge_notes": discharge_notes,
        "discharged_at": _now(),
    }
    _load_insert(_table_ref(hospital, DISCHARGES_TABLE), row)


# ---- billing --------------------------------------------------------------

def add_charge(
    hospital: str, encounter_id: str, patient_user_id: str, charge_type: str, description: str, amount: float
) -> None:
    row = {
        "charge_id": str(uuid.uuid4()),
        "encounter_id": encounter_id,
        "patient_user_id": patient_user_id,
        "charge_type": charge_type,
        "description": description,
        "amount": f"{amount:.2f}",
        "created_at": _now(),
    }
    _load_insert(_table_ref(hospital, BILLING_CHARGES_TABLE), row)


def list_charges_for_encounter(hospital: str, encounter_id: str) -> list[dict]:
    client = get_client()
    query = f"""
        SELECT charge_id, charge_type, description, amount, created_at
        FROM `{_table_ref(hospital, BILLING_CHARGES_TABLE)}`
        WHERE encounter_id = @encounter_id
        ORDER BY created_at
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("encounter_id", "STRING", encounter_id)]
    )
    return [dict(row) for row in client.query(query, job_config=job_config).result()]


def record_payment(hospital: str, encounter_id: str, patient_user_id: str, amount: float) -> None:
    row = {
        "payment_id": str(uuid.uuid4()),
        "encounter_id": encounter_id,
        "patient_user_id": patient_user_id,
        "amount": f"{amount:.2f}",
        "paid_at": _now(),
    }
    _load_insert(_table_ref(hospital, PAYMENTS_TABLE), row)


def list_payments_for_encounter(hospital: str, encounter_id: str) -> list[dict]:
    client = get_client()
    query = f"""
        SELECT payment_id, amount, paid_at
        FROM `{_table_ref(hospital, PAYMENTS_TABLE)}`
        WHERE encounter_id = @encounter_id
        ORDER BY paid_at
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("encounter_id", "STRING", encounter_id)]
    )
    return [dict(row) for row in client.query(query, job_config=job_config).result()]
