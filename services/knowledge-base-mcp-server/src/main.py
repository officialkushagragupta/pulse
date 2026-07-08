"""Entry point for the knowledge-base-mcp-server service.

Scaffolded in F1. The FastAPI application factory (shared foundation, F2) will be
wired here; ingest (K1), the hybrid retriever (K2), and the KB endpoints (K3) land
in this service. Run with:

    uv run uvicorn main:app --app-dir services/knowledge-base-mcp-server/src --reload
"""
