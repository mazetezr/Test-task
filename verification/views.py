import hashlib

from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import VerificationRequest
from .serializers import (
    VerificationRequestSerializer,
    VerificationRequestCreateSerializer,
    StatusUpdateSerializer,
)
from .filters import VerificationRequestFilter
from .tasks import check_new_request


class VerificationRequestViewSet(viewsets.ModelViewSet):
    """ViewSet для роботи із заявками на перевірку."""

    queryset = VerificationRequest.objects.all()
    serializer_class = VerificationRequestSerializer
    filterset_class = VerificationRequestFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'patch']

    def get_serializer_class(self):
        if self.action == 'create':
            return VerificationRequestCreateSerializer
        if self.action == 'update_status':
            return StatusUpdateSerializer
        return VerificationRequestSerializer

    # ── POST /api/requests/ ──────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone'].strip()
        address = serializer.validated_data['address'].strip().lower()

        # Перевірка дублікатів через Redis (TTL 10 хв)
        raw = f'{phone}:{address}'
        dedup_key = f'dedup:{hashlib.md5(raw.encode()).hexdigest()}'

        if cache.get(dedup_key):
            return Response(
                {'detail': 'Заявка з таким телефоном та адресою вже існує.'},
                status=status.HTTP_409_CONFLICT,
            )

        instance = serializer.save()
        cache.set(dedup_key, True, timeout=600)

        # Асинхронна перевірка через 2 хвилини
        check_new_request.apply_async(args=[instance.id], countdown=120)

        return Response(
            VerificationRequestSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    # ── PATCH /api/requests/<id>/status/ ─────────────────────────────
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        instance = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = instance.status
        instance.status = serializer.validated_data['status']
        instance.save()

        # WebSocket-повідомлення при зміні статусу
        if old_status != instance.status:
            from .services import NotificationService
            NotificationService.notify_status_change(instance, old_status)

        return Response(VerificationRequestSerializer(instance).data)

    # ── GET /api/requests/stats/ ─────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        now = timezone.now()
        day_ago = now - timedelta(hours=24)

        total = VerificationRequest.objects.count()
        by_status = dict(
            VerificationRequest.objects.values_list('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        last_24h = VerificationRequest.objects.filter(
            created_at__gte=day_ago
        ).count()

        return Response({
            'total': total,
            'by_status': {
                'new': by_status.get('new', 0),
                'in_progress': by_status.get('in_progress', 0),
                'verified': by_status.get('verified', 0),
                'rejected': by_status.get('rejected', 0),
            },
            'last_24h': last_24h,
        })
