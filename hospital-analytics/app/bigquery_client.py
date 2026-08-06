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


def insert_record(hospital: str, patient_user_id: str, staff_user_id: str, record_type: str, note: str) -> None:
    client = get_client()
    table = _table_ref(hospital, RECORDS_TABLE)
    row = {
        "record_id": str(uuid.uuid4()),
        "patient_user_id": patient_user_id,
        "staff_user_id": staff_user_id,
        "record_type": record_type,
        "note": note,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    errors = client.insert_rows_json(table, [row])
    if errors:
        raise RuntimeError(f"Failed to insert record into {table}: {errors}")


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
