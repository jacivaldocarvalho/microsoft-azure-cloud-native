"""Load the lab configuration from app/.env or the process environment."""

import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env", override=False)


def sql_settings():
    """Return the canonical SQL settings, accepting legacy initializer names."""
    server = os.getenv("SQL_SERVER")
    if not server and os.getenv("SQL_SERVER_NAME"):
        server = f"{os.environ['SQL_SERVER_NAME']}.database.windows.net"
    values = {
        "SQL_SERVER": server,
        "SQL_DATABASE": os.getenv("SQL_DATABASE") or os.getenv("SQL_DB_NAME"),
        "SQL_USERNAME": os.getenv("SQL_USERNAME") or os.getenv("SQL_USER"),
        "SQL_PASSWORD": os.getenv("SQL_PASSWORD"),
    }
    missing = [name for name, value in values.items() if not value or not value.strip()]
    if missing:
        raise ValueError("Missing environment variables: " + ", ".join(missing))
    return values
