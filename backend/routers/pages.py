from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.core.auth import read_session, COOKIE_NAME
from backend.services.system import get_stats
from backend.services.users import list_users

router = APIRouter()
templates = Jinja2Templates(directory="backend/web/templates")


def get_current_session(request: Request) -> dict | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    return read_session(token)


@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    session = get_current_session(request)
    return RedirectResponse("/dashboard" if session else "/login", status_code=302)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    session = get_current_session(request)
    if not session:
        return RedirectResponse("/login", status_code=302)

    stats = get_stats()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": session["u"], "role": session["r"], "stats": stats},
    )


@router.get("/users", response_class=HTMLResponse)
def users_page(request: Request):
    session = get_current_session(request)
    if not session:
        return RedirectResponse("/login", status_code=302)
    if session["r"] != "admin":
        return RedirectResponse("/dashboard", status_code=302)

    users = list_users()
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "user": session["u"], "role": session["r"], "users": users},
    )
