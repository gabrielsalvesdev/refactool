"""
Monitoring module for Refactool
"""
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from fastapi import Response

# Atualizei a configuração do exportador de métricas
reader = PrometheusMetricReader()
meter_provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(meter_provider)


def setup_observability(app):
    # Instrumenta a aplicação FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Expor o endpoint /metrics para Prometheus
    @app.get("/metrics")
    def prometheus_metrics():
        from prometheus_client import generate_latest
        return Response(generate_latest(), media_type="text/plain") 