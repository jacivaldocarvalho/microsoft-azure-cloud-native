"""Initialize the product table using the same SQL settings as Streamlit."""

import sys
from pathlib import Path

import pymssql

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import sql_settings


def main():
    try:
        settings = sql_settings()
        sql_script = Path(__file__).with_name("init.sql").read_text(encoding="utf-8")
        with pymssql.connect(
            server=settings["SQL_SERVER"],
            user=settings["SQL_USERNAME"],
            password=settings["SQL_PASSWORD"],
            database=settings["SQL_DATABASE"],
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_script)
                connection.commit()
        print("Database initialization completed.")
        return 0
    except Exception as exc:
        print(f"Database initialization failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
