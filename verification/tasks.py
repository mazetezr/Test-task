import logging

from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task
def check_new_request(request_id):
    """
    Перевірка заявки через 2 хвилини після створення.
    Якщо статус досі 'new' — відправити повідомлення в Telegram.
    """
    from .models import VerificationRequest
    from .services import NotificationService

    try:
        req = VerificationRequest.objects.get(id=request_id)
    except VerificationRequest.DoesNotExist:
        logger.warning(f'Заявку #{request_id} не знайдено')
        return

    if req.status == 'new':
        message = (
            f'⚠️ Заявка #{req.id} «{req.title}» '
            f'залишається у статусі "new" більше 2 хвилин.\n'
            f'Адреса: {req.address}\n'
            f'Телефон: {req.phone}'
        )
        NotificationService.send_telegram_message(message)
        logger.info(f'Повідомлення відправлено для заявки #{request_id}')
    else:
        logger.info(
            f'Заявка #{request_id} вже оброблена (статус: {req.status})'
        )


@shared_task
def check_stale_requests():
    """
    Періодична задача (Celery Beat, кожну хвилину).
    Перевіряє заявки у статусі 'in_progress', що не оновлювалися > 1 години.
    """
    from .models import VerificationRequest
    from .services import NotificationService

    threshold = timezone.now() - timedelta(hours=1)
    stale = VerificationRequest.objects.filter(
        status='in_progress',
        updated_at__lt=threshold,
    )

    count = 0
    for req in stale:
        message = (
            f'🔔 Нагадування: заявка #{req.id} «{req.title}» '
            f'у статусі "in_progress" більше 1 години.\n'
            f'Адреса: {req.address}\n'
            f'Остання зміна: {req.updated_at.strftime("%Y-%m-%d %H:%M")}'
        )
        NotificationService.send_telegram_message(message)
        count += 1

    if count:
        logger.info(f'Відправлено {count} нагадувань для застарілих заявок')
