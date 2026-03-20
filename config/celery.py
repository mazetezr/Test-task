import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat: перевірка застарілих заявок кожну хвилину
app.conf.beat_schedule = {
    'check-stale-requests': {
        'task': 'verification.tasks.check_stale_requests',
        'schedule': 60.0,
    },
}
