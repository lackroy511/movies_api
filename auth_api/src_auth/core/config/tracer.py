from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


def configure_tracer() -> None:
    resource = Resource.create(attributes={SERVICE_NAME: "auth_api"})

    provider = TracerProvider(resource=resource)

    jaeger_exporter = OTLPSpanExporter(endpoint="http://jaeger:4318/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    trace.set_tracer_provider(provider)
