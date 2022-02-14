from rest_framework import serializers

from . import models


class MetricSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Metric
        fields = ['id', 'pair', 'metric']


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Record
        fields = ['timestamp', 'value']
