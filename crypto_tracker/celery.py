import django
from django.conf import settings
import os

from celery import Celery
from celery.schedules import crontab
from kombu import Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_tracker.settings')
django.setup()

app = Celery('crypto_tracker')

app.conf.broker_url = 'redis://{}:6379/0'.format('localhost')
app.conf.result_backend = 'redis://{}:6379/0'.format('localhost')

app.conf.task_default_exchange = 'tasks'
app.conf.task_default_exchange_type = 'topic'
app.conf.task_default_routing_key = 'task.default'
app.conf.task_default_queue = 'tasks'
app.conf.task_queues = (
    Queue('tasks', routing_key='tasks.#'),
    Queue('transient', routing_key='transient.#', delivery_mode=1)
)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "fetch_metrics": {
        "task": "crypto_tracker.metrics.tasks.fetch_metrics",
        "schedule": crontab(minute="*/1"),
    },
}
app.conf.timezone = 'UTC'
app.conf.send_events = True
app.conf.result_extended = True
