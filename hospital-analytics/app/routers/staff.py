from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.bigquery_client import (
    create_encounter,
    get_hospital_info,
    get_patient_by_id,
    list_available_rooms,
    list_patients,
    list_recent_encounters,
    list_rooms,
)
from app.config import DEPARTMENTS, ENCOUNTER_TYPES, HOSPITALS
from app.deps import current_user_for
from app.templating import templates

router = APIRouter()


def _dashboard_context(hospital: str, user: dict, error: str | None = None) -> dict:
    total_rooms = list_rooms(hospital)
    available_rooms = list_available_rooms(hospital)
    return {
        "hospital": hospital,
        "hospital_name": HOSPITALS[hospital],
        "hospital_info": get_hospital_info(hospital),
        "user": user,
        "encounters": list_recent_encounters(hospital),
        "patients": list_patients(hospital),
        "encounter_types": ENCOUNTER_TYPES,
        "departments": DEPARTMENTS,
        "total_rooms": len(total_rooms),
        "occupied_rooms": len(total_rooms) - len(available_rooms),
        "error": error,
    }


@router.get("/{hospital}/staff/dashboard")
def staff_dashboard(request: Request, hospital: str, error: str | None = None):
    user = current_user_for(request, hospital, "staff")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    return templates.TemplateResponse(request, "staff_dashboard.html", _dashboard_context(hospital, user, error))


@router.post("/{hospital}/staff/encounters")
def admit_patient(
    request: Request,
    hospital: str,
    patient_user_id: str = Form(...),
    encounter_type: str = Form(...),
    department: str = Form(...),
    reason: str = Form(""),
    expected_discharge_date: str = Form(""),
):
    user = current_user_for(request, hospital, "staff")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    patient = get_patient_by_id(hospital, patient_user_id)
    if not patient or encounter_type not in ENCOUNTER_TYPES or department not in DEPARTMENTS:
        return templates.TemplateResponse(
            request,
            "staff_dashboard.html",
            _dashboard_context(hospital, user, "Could not admit patient — invalid patient, type, or department."),
            status_code=400,
        )

    encounter_id = create_encounter(
        hospital,
        patient_user_id=patient["user_id"],
        attending_staff_user_id=user["user_id"],
        encounter_type=encounter_type,
        reason=reason or None,
        department=department,
        expected_discharge_date=expected_discharge_date or None,
    )
    return RedirectResponse(f"/{hospital}/staff/encounters/{encounter_id}", status_code=303)
