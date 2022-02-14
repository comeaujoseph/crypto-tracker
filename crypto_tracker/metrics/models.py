from django.db import models

METRIC = [
    ("price", "price"),
]


class Metric(models.Model):

    key = models.CharField(max_length=25, null=False, blank=False)
    pair = models.CharField(max_length=25, null=False, blank=False)
    metric = models.CharField(max_length=15, blank=False, choices=METRIC, default="price")


class Record(models.Model):

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    value = models.FloatField(null=False)
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, db_index=True)
