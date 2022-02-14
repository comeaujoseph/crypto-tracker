"""Non-version specific API endpoints.

These endpoints are generally used for operational purposes (check service, status, etc.)
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


class CheckService(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response("OK", status=status.HTTP_200_OK)
