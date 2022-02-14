import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from crypto_tracker.metrics.management.commands.scheduler import fetch_metrics
from crypto_tracker.metrics.models import Metric, Record
from crypto_tracker.metrics.utils import standard_deviation, rank


class MetricTestCase(TestCase):

    def setUp(self):
        Metric.objects.create(key="btcusd", pair="BTC/USD", metric="price")

    def test_metric(self):
        m = Metric.objects.get(id=1)
        self.assertEqual(m.key, "btcusd")

    def test_metric_retrieval(self):
        fetch_metrics()
        records = Record.objects.filter(metric=1)
        self.assertGreater(len(records), 0)
        self.assertIsNotNone(records[0].value)

    def test_standard_deviation(self):
        m = Metric.objects.create(key="ltcusd", pair="LTC/USD", metric="price")
        timestamp = datetime.datetime.now()
        values = [42284.6, 42251.6, 42251.6, 42252.1, 42252.5, 42269.8, 42271.1, 42271.2, 42282.9]
        for v in values:
            Record(value=v, metric=m, timestamp=make_aware(timestamp)).save()
            timestamp -= datetime.timedelta(minutes=5)
        std_dev = standard_deviation(m.id)
        self.assertEqual(round(std_dev, 2), 12.84)

    def test_ranking(self):
        metric_id = 1
        expected_rank = 6
        standard_deviations = [
            {'id': 1, 'std_dev': 51.101513838175954}, {'id': 2, 'std_dev': 0.20770422018798892},
            {'id': 3, 'std_dev': 0.10302515916763601}, {'id': 4, 'std_dev': 2.7245235309402833e-05},
            {'id': 5, 'std_dev': 35.34235954818003}, {'id': 6, 'std_dev': 3.1502608401604073}
        ]
        self.assertEqual(rank(metric_id, standard_deviations), expected_rank)
