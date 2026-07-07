import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_str):
    try:
        access_token = AccessToken(token_str)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except Exception:
        return None


class CallConsumer(AsyncWebsocketConsumer):
    """
    Basic WebRTC signaling relay.
    Browser connects to: ws://<host>/ws/call/<room_name>/?token=<jwt_access_token>

    This server does NOT handle the actual audio/video stream (that's peer-to-peer
    WebRTC between browsers) - it only relays the small JSON signaling messages
    (offer / answer / ICE candidates / mute state) needed to set that connection up.
    """

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'call_{self.room_name}'

        # Pull JWT out of the query string since browsers can't send custom
        # Authorization headers on a WebSocket handshake.
        query_string = self.scope.get('query_string', b'').decode()
        params = dict(p.split('=') for p in query_string.split('&') if '=' in p)
        token = params.get('token')

        user = await get_user_from_token(token) if token else None
        if not user:
            await self.close(code=4001)  # unauthorized
            return

        self.user = user

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Tell everyone else already in the room that a new peer joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_message',
                'sender_channel': self.channel_name,
                'message': {
                    'event': 'peer-joined',
                    'user_id': user.id,
                    'name': user.name,
                }
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_message',
                    'sender_channel': self.channel_name,
                    'message': {
                        'event': 'peer-left',
                        'user_id': getattr(self, 'user', None) and self.user.id,
                    }
                }
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        # Just relay whatever signaling payload the frontend sends
        # (offer / answer / ice-candidate / toggle-audio / toggle-video)
        # to every other participant in the same room.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_message',
                'sender_channel': self.channel_name,
                'message': data,
            }
        )

    async def call_message(self, event):
        # Don't echo a message back to the person who sent it
        if event['sender_channel'] == self.channel_name:
            return
        await self.send(text_data=json.dumps(event['message']))
