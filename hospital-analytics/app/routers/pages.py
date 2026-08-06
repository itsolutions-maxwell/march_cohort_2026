from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.config import HOSPITALS
from app.templating import templates

router = APIRouter()


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"hospitals": HOSPITALS})


@router.get("/{hospital}/login")
def login_page(request: Request, hospital: str):
    if hospital not in HOSPITALS:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"hospital": hospital, "hospital_name": HOSPITALS[hospital], "error": None},
    )
