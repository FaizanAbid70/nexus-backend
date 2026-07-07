"""
ASGI config for nexus_backend project.

Routes plain HTTP requests to Django as normal, and routes WebSocket
connections (used for the video call signaling in Milestone 4) to the
`calls` app's consumer.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexus_backend.settings')

# This has to happen before importing anything that touches Django models
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
import calls.routing  # noqa: E402

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(calls.routing.websocket_urlpatterns),
})
