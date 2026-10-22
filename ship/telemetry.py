"""OpenTelemetry setup shared by the Holodeck and the Ship processes."""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter


def setup_tracing(service_name: str, exporter: SpanExporter | None = None) -> TracerProvider:
    """Install the global tracer provider. Without an exporter, spans go over OTLP gRPC to
    `OTEL_EXPORTER_OTLP_ENDPOINT`; with one (tests), each span is exported as it ends."""
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    if exporter is None:
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    else:
        provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider
