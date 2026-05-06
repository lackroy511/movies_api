from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from src_auth.core.config.settings import settings


def configure_tracer() -> None:
    resource = Resource.create(attributes={SERVICE_NAME: settings.jaeger_service_name})

    provider = TracerProvider(resource=resource)

    jaeger_exporter = OTLPSpanExporter(endpoint=settings.jaeger_tracer_path)
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    trace.set_tracer_provider(provider)
