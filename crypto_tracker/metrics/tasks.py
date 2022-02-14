""""""

from celery import shared_task
import cryptowatch
from django.conf import settings
import logging

from crypto_tracker.metrics import models as metrics_model

log = logging.getLogger(__name__)


@shared_task(soft_time_limit=60)
def fetch_metrics(**kwargs):
    # TODO: Error handling
    #   Resource not found (i.e. bad exchange or pair)
    log.debug("Fetching the latest cryptocurrency quotes...")
    metrics = metrics_model.Metric.objects.all()
    for metric in metrics:
        summary = cryptowatch.markets.get(
            "{exchange}:{pair}".format(exchange=settings.EXCHANGE, pair=metric.key)
        )
        price = summary.market.price.last
        # Record the price for metric
        metrics_model.Record(value=price, metric=metric).save()
    log.debug("Cryptocurrency quotes have been updated.")








