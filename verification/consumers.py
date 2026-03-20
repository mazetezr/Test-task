import json

from channels.generic.websocket import AsyncWebsocketConsumer


class VerificationConsumer(AsyncWebsocketConsumer):
    """WebSocket для отримання оновлень статусу заявок у реальному часі."""

    async def connect(self):
        await self.channel_layer.group_add(
            'verification_requests',
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'verification_requests',
            self.channel_name,
        )

    async def status_update(self, event):
        """Обробка повідомлення про зміну статусу."""
        await self.send(text_data=json.dumps(event['data']))
