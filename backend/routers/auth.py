from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.core.auth import COOKIE_NAME, create_session, read_session
from backend.core.security import verify_password
from backend.services.users import get_user_by_username

router = APIRouter()
templates = Jinja2Templates(directory="backend/web/templates")


def get_current_session(request: Request) -> dict | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    return read_session(token)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # si ya está logueado, directo al dashboard
    if get_current_session(request):
        return RedirectResponse("/dashboard", status_code=302)

    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = get_user_by_username(username)
    if user and user.get("is_active") == 1:
        if verify_password(password, user["password_hash"]):
            resp = RedirectResponse("/dashboard", status_code=302)
            resp.set_cookie(
                COOKIE_NAME,
                create_session(user["username"], user["role"]),
                httponly=True,
                samesite="lax",
            )
            return resp

    return RedirectResponse("/login?error=1", status_code=302)


@router.get("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie(COOKIE_NAME)
    return resp
