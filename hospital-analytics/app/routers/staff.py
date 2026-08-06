from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.bigquery_client import get_patient_by_id, insert_record, list_patients, list_recent_records
from app.config import HOSPITALS
from app.deps import current_user_for
from app.templating import templates

router = APIRouter()


@router.get("/{hospital}/staff/dashboard")
def staff_dashboard(request: Request, hospital: str, error: str | None = None):
    user = current_user_for(request, hospital, "staff")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    records = list_recent_records(hospital)
    patients = list_patients(hospital)
    return templates.TemplateResponse(
        request,
        "staff_dashboard.html",
        {
            "hospital": hospital,
            "hospital_name": HOSPITALS[hospital],
            "user": user,
            "records": records,
            "patients": patients,
            "error": error,
        },
    )


@router.post("/{hospital}/staff/records")
def create_record(
    request: Request,
    hospital: str,
    patient_user_id: str = Form(...),
    record_type: str = Form(...),
    note: str = Form(...),
):
    user = current_user_for(request, hospital, "staff")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    patient = get_patient_by_id(hospital, patient_user_id)
    if not patient:
        records = list_recent_records(hospital)
        patients = list_patients(hospital)
        return templates.TemplateResponse(
            request,
            "staff_dashboard.html",
            {
                "hospital": hospital,
                "hospital_name": HOSPITALS[hospital],
                "user": user,
                "records": records,
                "patients": patients,
                "error": "Selected patient was not found at this hospital.",
            },
            status_code=400,
        )

    insert_record(
        hospital,
        patient_user_id=patient["user_id"],
        staff_user_id=user["user_id"],
        record_type=record_type,
        note=note,
    )
    return RedirectResponse(f"/{hospital}/staff/dashboard", status_code=303)
