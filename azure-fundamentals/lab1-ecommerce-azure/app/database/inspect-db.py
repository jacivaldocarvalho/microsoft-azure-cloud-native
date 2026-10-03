"""Inspect the lab database schema and stored products from the command line."""

import argparse
import sys
from pathlib import Path

import pymssql

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import sql_settings


SCHEMA_QUERY = """
SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'Produtos'
ORDER BY ORDINAL_POSITION
"""

PRODUCTS_QUERY = """
SELECT id, nome, descricao, preco, imagem_url
FROM dbo.Produtos
ORDER BY id
"""


def print_table(headers, rows):
    values = [["" if value is None else str(value) for value in row] for row in rows]
    widths = [
        max([len(header), *(len(row[index]) for row in values)])
        for index, header in enumerate(headers)
    ]
    template = " | ".join(f"{{:<{width}}}" for width in widths)
    print(template.format(*headers))
    print("-+-".join("-" * width for width in widths))
    for row in values:
        print(template.format(*row))


def inspect(section):
    settings = sql_settings()
    query, headers = {
        "schema": (
            SCHEMA_QUERY,
            ["column", "type", "max_length", "nullable"],
        ),
        "products": (
            PRODUCTS_QUERY,
            ["id", "name", "description", "price", "image_url"],
        ),
    }[section]

    with pymssql.connect(
        server=settings["SQL_SERVER"],
        user=settings["SQL_USERNAME"],
        password=settings["SQL_PASSWORD"],
        database=settings["SQL_DATABASE"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    print_table(headers, rows)


def main():
    parser = argparse.ArgumentParser(
        description="Inspect the Produtos table without exposing credentials."
    )
    parser.add_argument("section", choices=("schema", "products"))
    args = parser.parse_args()
    try:
        inspect(args.section)
        return 0
    except Exception as exc:
        print(f"Database inspection failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
