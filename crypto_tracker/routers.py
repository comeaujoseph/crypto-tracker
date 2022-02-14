from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter(trailing_slash=False)

from crypto_tracker.metrics.views import MetricsViewSet

router_v1.register(r"metrics", MetricsViewSet, basename='metrics')
