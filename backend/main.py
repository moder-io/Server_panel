from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.db import init_db
from backend.core.config import DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASS, DEFAULT_ADMIN_ROLE
from backend.services.users import ensure_default_admin

from backend.routers.pages import router as pages_router
from backend.routers.auth import router as auth_router
from backend.routers.stats import router as stats_router
from backend.routers.services import router as services_router
from backend.routers.users import router as users_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="backend/web/static"), name="static")
templates = Jinja2Templates(directory="backend/web/templates")


@app.on_event("startup")
def on_startup():
    init_db()
    ensure_default_admin(DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASS, DEFAULT_ADMIN_ROLE)


def wants_html(request: Request) -> bool:
    accept = (request.headers.get("accept") or "").lower()

    # Si el cliente pide JSON explícitamente, devolvemos JSON
    if "application/json" in accept:
        return False

    # Para rutas API, por defecto JSON (salvo que el cliente pida HTML explícitamente)
    if request.url.path.startswith("/api"):
        return "text/html" in accept

    # Para páginas normales, HTML
    return "text/html" in accept or "*/*" in accept


def render_error_page(request: Request, status_code: int, message: str, detail: str | None = None):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": status_code,
            "message": message,
            "detail": detail,
        },
        status_code=status_code,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if wants_html(request):
        return render_error_page(
            request,
            status_code=exc.status_code,
            message="Ha ocurrido un error al procesar la solicitud.",
            detail=str(exc.detail) if exc.detail else None,
        )
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if wants_html(request):
        return render_error_page(
            request,
            status_code=422,
            message="Los datos enviados no son válidos.",
            detail=str(exc),
        )
    return JSONResponse({"error": "validation_error", "detail": exc.errors()}, status_code=422)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if wants_html(request):
        return render_error_page(
            request,
            status_code=500,
            message="Error interno del servidor.",
            detail=str(exc),
        )
    return JSONResponse({"error": "internal_server_error"}, status_code=500)


# Routers
app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(stats_router)
app.include_router(services_router)
app.include_router(users_router)
