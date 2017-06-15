from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from . import models as m

admin.site.unregister(User)

class ProfileInline(admin.TabularInline):
    model = m.Profile
    fields = ['logon_attributes_token',]


class PreferenceInline(admin.TabularInline):
    model = m.Preference
    fields = ['group', 'key', 'val']
    extra = 1


@admin.register(User)
class UserAdminPlus(UserAdmin):
    inlines = [ProfileInline, PreferenceInline]

    actions = ['generate_notifications']

    def generate_notifications(self, request, queryset):
        for user in queryset:
            user.profile.generate_notifications()

