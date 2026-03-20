from django.contrib import admin

from .models import VerificationRequest


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'phone', 'source', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'source']
    search_fields = ['title', 'address', 'phone']
    readonly_fields = ['created_at', 'updated_at']
