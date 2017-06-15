from django.contrib import admin
from . import models as m


@admin.register(m.PhaseMetadata)
class PhaseMetadataAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'content']
    exclude = ('modified_by',)
    actions = None

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        obj.save()


@admin.register(m.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['phase', 'email', 'due_date', 'created_at', 'status']
    list_filter = ['phase', 'status']
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'
    actions = ['send_email']

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def send_email(self, request, queryset):
        for n in queryset:
            n.send()
    send_email.short_description = "Send email for selected notifications"
