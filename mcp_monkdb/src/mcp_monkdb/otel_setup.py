import os
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def configure_otel():
    if os.getenv("MONKDB_OTEL_ENABLED", "false").lower() != "true":
        return

    endpoint = os.getenv(
        "MONKDB_OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    service_name = os.getenv("MONKDB_OTEL_SERVICE_NAME", "mcp-monkdb")
    auth_header = os.getenv("MONKDB_OTEL_AUTH_HEADER", "")

    headers = {}
    if auth_header:
        try:
            key, value = auth_header.split("=", 1)
            headers[key.strip()] = value.strip()
        except ValueError:
            print("Invalid MONKDB_OTEL_AUTH_HEADER format. Expected: Key=Value")

    resource = Resource(attributes={SERVICE_NAME: service_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

    RequestsInstrumentor().instrument()
