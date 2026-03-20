from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VerificationRequestViewSet

router = DefaultRouter()
router.register(r'requests', VerificationRequestViewSet, basename='request')

urlpatterns = [
    path('', include(router.urls)),
]
