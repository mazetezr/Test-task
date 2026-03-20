from rest_framework import serializers

from .models import VerificationRequest


class VerificationRequestSerializer(serializers.ModelSerializer):
    """Серіалізатор для читання заявок (список / деталі)."""

    class Meta:
        model = VerificationRequest
        fields = '__all__'
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class VerificationRequestCreateSerializer(serializers.ModelSerializer):
    """Серіалізатор для створення заявки."""

    class Meta:
        model = VerificationRequest
        fields = ['title', 'address', 'phone', 'source', 'comment']


class StatusUpdateSerializer(serializers.Serializer):
    """Серіалізатор для зміни статусу заявки."""

    status = serializers.ChoiceField(choices=VerificationRequest.STATUS_CHOICES)
