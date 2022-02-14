import logging

import cryptowatch

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from crypto_tracker.metrics import models as metrics_model

log = logging.getLogger(__name__)


def fetch_metrics():
    # TODO: Error handling
    #   Resource not found (i.e. bad exchange or pair)
    log.info("Fetching the latest cryptocurrency quotes...")
    metrics = metrics_model.Metric.objects.all()
    for metric in metrics:
        summary = cryptowatch.markets.get(
            "{exchange}:{pair}".format(exchange=settings.EXCHANGE, pair=metric.key)
        )
        price = summary.market.price.last
        # Record the price for metric
        metrics_model.Record(value=price, metric=metric).save()
    log.info("Cryptocurrency quotes have been updated.")


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after our job has run.
@util.close_old_connections
def delete_old_job_executions(max_age=86400):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 1 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            fetch_metrics,
            trigger=CronTrigger(minute="*/1"),  # Every 10 seconds
            id="fetch_metrics",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=False,
        )

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )

        try:
            log.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            log.info("Stopping scheduler...")
            scheduler.shutdown()
            log.info("Scheduler shut down successfully!")
