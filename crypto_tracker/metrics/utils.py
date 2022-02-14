
import datetime

from django.db.models.aggregates import StdDev
from django.utils.timezone import make_aware

from . import models


def standard_deviation(metric_id):
    std_dev = models.Record.objects.filter(
        metric=metric_id,
        timestamp__gte=make_aware(datetime.datetime.now() - datetime.timedelta(days=1))
    ).aggregate(StdDev('value')).get('value__stddev', 0)
    return 0 if std_dev is None else std_dev


def rank(metric_id, standard_deviations):
    # rank metrics - sorts the list of metrics in ascending order of standard deviation
    ranks = sorted(standard_deviations, key=lambda i: i['std_dev'])
    # Return the rank for selected metric
    return next((i for i, item in enumerate(ranks) if item["id"] == metric_id), None) + 1

