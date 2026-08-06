from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.bigquery_client import list_records_for_patient
from app.config import HOSPITALS
from app.deps import current_user_for
from app.templating import templates

router = APIRouter()


@router.get("/{hospital}/patient/dashboard")
def patient_dashboard(request: Request, hospital: str):
    user = current_user_for(request, hospital, "patient")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    records = list_records_for_patient(hospital, user["user_id"])
    return templates.TemplateResponse(
        request,
        "patient_dashboard.html",
        {
            "hospital": hospital,
            "hospital_name": HOSPITALS[hospital],
            "user": user,
            "records": records,
        },
    )
