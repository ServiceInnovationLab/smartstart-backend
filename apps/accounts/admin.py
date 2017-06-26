from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from . import models as m

admin.site.unregister(User)

class ProfileInline(admin.StackedInline):
    model = m.Profile
    fields = [
        'subscribed',
        'logon_attributes_token',
    ]


class PreferenceInline(admin.TabularInline):
    model = m.Preference
    fields = ['group', 'key', 'val']
    extra = 1


@admin.register(User)
class UserAdminPlus(UserAdmin):
    list_display = ['username', 'date_joined', 'email', 'subscribed', 'due_date']
    inlines = [ProfileInline, PreferenceInline]
    date_hierarchy = 'date_joined'

    actions = ['generate_notifications']

    def generate_notifications(self, request, queryset):
        for user in queryset:
            user.profile.generate_notifications()

    def due_date(self, user):
        helper = user.profile.get_pregnancy_helper()
        if helper:
            phase = helper.get_due_phase(weeks_before=0)
            return '{}({} weeks, phase {})'.format(
                helper.due_date,
                helper.get_weekno(),
                phase.id if phase else '-',
            )

    def subscribed(self, user):
        return user.profile.subscribed
