#!/bin/sh

if [ -z "$(find migrations/versions -mindepth 1 -maxdepth 1 -type f ! -name '__init__.py' -print -quit)" ]; then
  echo "No migrations found, generating initial migration"
  poetry run alembic revision --autogenerate -m "Initial migration"
fi

poetry run alembic upgrade head

exec poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload