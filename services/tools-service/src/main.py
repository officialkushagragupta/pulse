"""Entry point for the tools-service.

    uv run uvicorn main:app --app-dir services/tools-service/src --reload
"""
from api.app import create_app

app = create_app()
