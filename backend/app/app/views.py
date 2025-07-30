"""
Heathcheck view for the app.
"""

from rest_framework import generics
from rest_framework.response import Response



class HealthCheckView(generics.GenericAPIView):
    """Health check view to verify the app is running."""

    def get(self, request, *args, **kwargs):
        """Return a simple response indicating the app is healthy."""
        return Response({"status": "ok"}, status=200)
