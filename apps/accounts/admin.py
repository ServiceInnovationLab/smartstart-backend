from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from . import models as m
admin.site.unregister(User)


class PreferenceInline(admin.TabularInline):
    model = m.Preference
    fields = ['group', 'key', 'val']
    extra = 1


class EmailAddressInline(admin.TabularInline):
    model = m.EmailAddress
    fields = ['email']
    extra = 1


@admin.register(m.UserProxy)
class UserProxyAdmin(UserAdmin):
    list_display = ['username', 'date_joined', 'email', 'subscribed', 'due_date']
    inlines = [PreferenceInline, EmailAddressInline]
    date_hierarchy = 'date_joined'

    actions = ['generate_notifications']

    def generate_notifications(self, request, queryset):
        for user in queryset:
            user.profile.generate_notifications()

    def due_date(self, user):
        helper = user.get_pregnancy_helper()
        if helper:
            phase = helper.get_due_phase(weeks_before=0)
            return '{}({} weeks, phase {})'.format(
                helper.due_date,
                helper.get_weekno(),
                phase.id if phase else '-',
            )

    def subscribed(self, user):
        return user.profile.subscribed


@admin.register(m.EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'created_at']
    raw_id_fields = ['user']
