from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.bigquery_client import (
    add_treatment,
    assign_room,
    discharge_encounter,
    get_current_room,
    get_encounter,
    list_available_rooms,
    list_charges_for_encounter,
    list_treatments_for_encounter,
)
from app.config import HOSPITALS
from app.deps import current_user_for
from app.templating import templates

router = APIRouter()


def _detail_context(hospital: str, encounter: dict, user: dict, error: str | None = None) -> dict:
    return {
        "hospital": hospital,
        "hospital_name": HOSPITALS[hospital],
        "user": user,
        "encounter": encounter,
        "current_room": get_current_room(hospital, encounter["encounter_id"]),
        "treatments": list_treatments_for_encounter(hospital, encounter["encounter_id"]),
        "charges": list_charges_for_encounter(hospital, encounter["encounter_id"]),
        "available_rooms": [] if encounter["is_discharged"] else list_available_rooms(hospital),
        "error": error,
    }


@router.get("/{hospital}/staff/encounters/{encounter_id}")
def encounter_detail(request: Request, hospital: str, encounter_id: str):
    user = current_user_for(request, hospital, "staff")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    encounter = get_encounter(hospital, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    return templates.TemplateResponse(request, "encounter_detail.html", _detail_context(hospital, encounter, user))


@router.post("/{hospital}/staff/encounters/{encounter_id}/rooms")
def assign_encounter_room(request: Request, hospital: str, encounter_id: str, room_id: str = Form(...)):
    user = current_user_for(request, hospital, "staff")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    encounter = get_encounter(hospital, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    available_room_ids = {r["room_id"] for r in list_available_rooms(hospital)}
    if encounter["is_discharged"] or room_id not in available_room_ids:
        return templates.TemplateResponse(
            request,
            "encounter_detail.html",
            _detail_context(hospital, encounter, user, error="That room isn't available to assign."),
            status_code=400,
        )

    assign_room(
        hospital,
        encounter_id,
        room_id,
        staff_user_id=user["user_id"],
        patient_user_id=encounter["patient_user_id"],
    )
    return RedirectResponse(f"/{hospital}/staff/encounters/{encounter_id}", status_code=303)


@router.post("/{hospital}/staff/encounters/{encounter_id}/treatments")
def add_encounter_treatment(
    request: Request,
    hospital: str,
    encounter_id: str,
    treatment_type: str = Form(...),
    notes: str = Form(""),
):
    user = current_user_for(request, hospital, "staff")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    encounter = get_encounter(hospital, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    if encounter["is_discharged"]:
        return templates.TemplateResponse(
            request,
            "encounter_detail.html",
            _detail_context(hospital, encounter, user, error="This encounter is already discharged."),
            status_code=400,
        )

    add_treatment(
        hospital,
        encounter_id,
        staff_user_id=user["user_id"],
        treatment_type=treatment_type,
        notes=notes or None,
        patient_user_id=encounter["patient_user_id"],
    )
    return RedirectResponse(f"/{hospital}/staff/encounters/{encounter_id}", status_code=303)


@router.post("/{hospital}/staff/encounters/{encounter_id}/discharge")
def discharge(request: Request, hospital: str, encounter_id: str, discharge_notes: str = Form("")):
    user = current_user_for(request, hospital, "staff")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    encounter = get_encounter(hospital, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    if encounter["is_discharged"]:
        return templates.TemplateResponse(
            request,
            "encounter_detail.html",
            _detail_context(hospital, encounter, user, error="This encounter is already discharged."),
            status_code=400,
        )

    discharge_encounter(hospital, encounter_id, staff_user_id=user["user_id"], discharge_notes=discharge_notes or None)
    return RedirectResponse(f"/{hospital}/staff/encounters/{encounter_id}", status_code=303)
