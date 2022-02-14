""""""

import datetime
from django.utils.timezone import make_aware
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from crypto_tracker.base.permissions import ReadOnly

from . import models
from . import serializers
from . import utils


######################################################
# Metrics
######################################################


class MetricsViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Metric.objects.all()
    serializer_class = serializers.MetricSerializer
    permission_classes = [ReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # calculate standard deviation for the metrics
        std_dev = [{'id': m.id, 'std_dev': utils.standard_deviation(m)} for m in models.Metric.objects.all()]
        rank = utils.rank(instance.id, std_dev)

        data = dict(rank=rank)
        data.update(self.get_serializer(instance).data)
        return Response(data)

    @action(methods=['GET'], detail=True)
    def records(self, request, *args, **kwargs):
        instance = self.get_object()
        records = models.Record.objects.filter(
            metric=instance.id,
            timestamp__gte=make_aware(datetime.datetime.now() - datetime.timedelta(days=1))
        )
        return Response(serializers.RecordSerializer(records, many=True).data)
