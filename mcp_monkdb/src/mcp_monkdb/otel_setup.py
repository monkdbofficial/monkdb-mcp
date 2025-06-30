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

    resource = Resource(attributes={SERVICE_NAME: service_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    RequestsInstrumentor().instrument()
