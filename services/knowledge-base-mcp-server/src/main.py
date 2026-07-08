"""Entry point for the knowledge-base-mcp-server.

    uv run uvicorn main:app --app-dir services/knowledge-base-mcp-server/src --reload
"""
from api.app import create_app

app = create_app()
