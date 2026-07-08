"""Entry point for the mcp-client service.

    uv run uvicorn main:app --app-dir services/mcp-client/src --reload
"""
from api.app import create_app

app = create_app()
