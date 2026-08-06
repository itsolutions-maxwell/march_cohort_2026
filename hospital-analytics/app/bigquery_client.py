import uuid
from datetime import datetime, timezone
from functools import lru_cache

from google.cloud import bigquery

from app.config import settings

USERS_TABLE = "users"
RECORDS_TABLE = "records"


@lru_cache
def get_client() -> bigquery.Client:
    return bigquery.Client(project=settings.gcp_project_id)


def _table_ref(hospital: str, table: str) -> str:
    return f"{settings.gcp_project_id}.{hospital}.{table}"


# BigQuery projects without billing enabled reject both the streaming
# insert API ("Streaming insert is not allowed in the free tier") and DML
# INSERT ("DML queries are not allowed in the free tier"). A load job is
# the one write path that's free-tier-safe, so all writes go through
# load_table_from_json against the table's existing schema.
def _load_insert(table: str, row: dict) -> None:
    client = get_client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    client.load_table_from_json([row], table, job_config=job_config).result()


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


def insert_record(hospital: str, patient_user_id: str, staff_user_id: str, record_type: str, note: str) -> None:
    row = {
        "record_id": str(uuid.uuid4()),
        "patient_user_id": patient_user_id,
        "staff_user_id": staff_user_id,
        "record_type": record_type,
        "note": note,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _load_insert(_table_ref(hospital, RECORDS_TABLE), row)


def insert_user(hospital: str, user_id: str, email: str, password_hash: str, role: str, full_name: str) -> None:
    row = {
        "user_id": user_id,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "full_name": full_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _load_insert(_table_ref(hospital, USERS_TABLE), row)


def list_recent_records(hospital: str, limit: int = 50) -> list[dict]:
    client = get_client()
    query = f"""
        SELECT record_id, patient_user_id, staff_user_id, record_type, note, created_at
        FROM `{_table_ref(hospital, RECORDS_TABLE)}`
        ORDER BY created_at DESC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("limit", "INT64", limit)]
    )
    return [dict(row) for row in client.query(query, job_config=job_config).result()]


def list_records_for_patient(hospital: str, patient_user_id: str, limit: int = 50) -> list[dict]:
    client = get_client()
    query = f"""
        SELECT record_id, record_type, note, created_at
        FROM `{_table_ref(hospital, RECORDS_TABLE)}`
        WHERE patient_user_id = @patient_user_id
        ORDER BY created_at DESC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("patient_user_id", "STRING", patient_user_id),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    return [dict(row) for row in client.query(query, job_config=job_config).result()]
