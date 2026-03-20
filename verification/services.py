import logging

import requests as http_requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервіс відправки повідомлень (Telegram + WebSocket)."""

    @staticmethod
    def send_telegram_message(message):
        """Відправка повідомлення в Telegram або логування, якщо бот не налаштований."""
        token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID

        if not token or not chat_id:
            logger.info(f'[Telegram] Повідомлення (логування): {message}')
            return

        try:
            url = f'https://api.telegram.org/bot{token}/sendMessage'
            response = http_requests.post(url, json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
            })
            response.raise_for_status()
            logger.info('[Telegram] Повідомлення успішно відправлено')
        except Exception as e:
            logger.error(f'[Telegram] Помилка відправки: {e}')

    @staticmethod
    def notify_status_change(request_obj, old_status):
        """Відправка WebSocket-повідомлення про зміну статусу."""
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'verification_requests',
                {
                    'type': 'status_update',
                    'data': {
                        'id': request_obj.id,
                        'title': request_obj.title,
                        'old_status': old_status,
                        'new_status': request_obj.status,
                    }
                }
            )
        except Exception as e:
            logger.error(f'[WebSocket] Помилка відправки: {e}')
