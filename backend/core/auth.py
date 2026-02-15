from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from .config import SECRET_KEY, SESSION_MAX_AGE

COOKIE_NAME = "sp_session"

_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="server_panel_session")

def create_session(username: str, role: str) -> str:
    return _serializer.dumps({"u": username, "r": role})

def read_session(token: str) -> dict | None:
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE)
        if not isinstance(data, dict):
            return None
        if not isinstance(data.get("u"), str):
            return None
        if data.get("r") not in {"admin", "viewer"}:
            return None
        return data
    except (BadSignature, SignatureExpired):
        return None
