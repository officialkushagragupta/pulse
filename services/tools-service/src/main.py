"""Entry point for the tools-service.

Scaffolded in F1. The FastAPI application factory (shared foundation, F2) will be
wired here, and the composition root in ``api/dependencies.py`` (T10) will inject
concrete adapters into the use cases. Run with:

    uv run uvicorn main:app --app-dir services/tools-service/src --reload
"""
