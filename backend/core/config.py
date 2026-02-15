import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

DB_PATH = os.getenv("DB_PATH", "server_panel.db")

SESSION_MAX_AGE = int(os.getenv("SESSION_MAX_AGE", "604800"))  # 7 días

DEFAULT_ADMIN_USER = os.getenv("DEFAULT_ADMIN_USER", "admin")
DEFAULT_ADMIN_PASS = os.getenv("DEFAULT_ADMIN_PASS", "admin123")
DEFAULT_ADMIN_ROLE = os.getenv("DEFAULT_ADMIN_ROLE", "admin")
