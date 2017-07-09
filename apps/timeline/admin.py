from django.contrib import admin
from . import models as m


@admin.register(m.PhaseMetadata)
class PhaseMetadataAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'content']
    actions = None

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(m.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['phase', 'email', 'pregnancy_date', 'due_date', 'weekno', 'created_at', 'status']
    list_filter = ['phase', 'status']
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'
    actions = ['send_email']

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def send_email(self, request, queryset):
        m.Notification.objects.send_all(notifications=queryset)
    send_email.short_description = "Send email for selected notifications"
