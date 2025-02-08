from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricExporter
from fastapi import Response

# Configurar o exportador de métricas para o Prometheus
exporter = PrometheusMetricExporter()
meter_provider = MeterProvider([PeriodicExportingMetricReader(exporter)])
metrics.set_meter_provider(meter_provider)


def setup_observability(app):
    # Instrumenta a aplicação FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Expor o endpoint /metrics para Prometheus
    @app.get("/metrics")
    def prometheus_metrics():
        from prometheus_client import generate_latest
        return Response(generate_latest(), media_type="text/plain") 