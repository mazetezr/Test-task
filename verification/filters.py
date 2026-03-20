import django_filters

from .models import VerificationRequest


class VerificationRequestFilter(django_filters.FilterSet):
    """Фільтрація заявок по статусу та джерелу."""

    class Meta:
        model = VerificationRequest
        fields = ['status', 'source']
