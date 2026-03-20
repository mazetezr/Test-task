from django.db import models


class VerificationRequest(models.Model):
    """Заявка на перевірку об'єкта нерухомості."""

    SOURCE_CHOICES = [
        ('olx', 'OLX'),
        ('telegram', 'Telegram'),
        ('manual', 'Вручну'),
    ]
    STATUS_CHOICES = [
        ('new', 'Нова'),
        ('in_progress', 'В обробці'),
        ('verified', 'Перевірена'),
        ('rejected', 'Відхилена'),
    ]

    title = models.CharField('Назва', max_length=255)
    address = models.TextField('Адреса')
    phone = models.CharField('Телефон', max_length=50)
    source = models.CharField('Джерело', max_length=20, choices=SOURCE_CHOICES)
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default='new'
    )
    comment = models.TextField('Коментар', blank=True, default='')
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка на перевірку'
        verbose_name_plural = 'Заявки на перевірку'

    def __str__(self):
        return f'#{self.id} {self.title} ({self.get_status_display()})'
