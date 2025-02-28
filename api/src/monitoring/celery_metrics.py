from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader

# Configurar o provider com PrometheusMetricReader
reader = PrometheusMetricReader()
provider = MeterProvider(metric_readers=[reader])
set_meter_provider(provider)

meter = get_meter_provider().get_meter("celery_tasks")

# Cria um histograma para medir a duração das tasks
task_duration = meter.create_histogram(
    name="celery.task.duration",
    description="Duração das tasks em segundos",
    unit="s"
)

# Cria um counter para contar falhas das tasks
task_failures = meter.create_counter(
    name="celery.task.failures",
    description="Total de falhas por tipo de task",
    unit="1"
)

warnings_counter = meter.create_counter(
    name="code_analysis_warnings_total",
    description="Total de warnings por tipo"
)

cache_hits = meter.create_counter(
    name="redis_cache_hits_total",
    description="Total de acertos no cache"
)

cache_misses = meter.create_counter(
    name="redis_cache_misses_total",
    description="Total de misses no cache"
)

from celery import signals

@signals.task_postrun.connect
def track_task_metrics(task_id, task, **kwargs):
    labels = {"task_name": task.name}
    if getattr(task, 'failed', False):
        task_failures.add(1, labels)
    else:
        # Calcula a duração da task se os timestamps estiverem disponíveis
        date_started = getattr(task, 'date_started', None)
        date_done = getattr(task, 'date_done', None)
        if date_started and date_done:
            duration = (date_done - date_started).total_seconds()
            task_duration.record(duration, labels) 