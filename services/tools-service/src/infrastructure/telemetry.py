"""OpenTelemetry tracing setup.

A TracerProvider is always installed so every request span mints a valid
trace_id/span_id (used for log correlation). Spans are exported via OTLP only when
OTEL_EXPORTER_OTLP_ENDPOINT is set (production); in dev there is no exporter, so no
console noise, but correlation ids still flow into the logs.
"""
import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_configured = False


def configure_telemetry(service_name: str) -> None:
    global _configured
    if _configured:
        return
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    _configured = True
