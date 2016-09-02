from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from . import models as m

admin.site.unregister(User)

class ProfileInline(admin.TabularInline):
    model = m.Profile
    fields = ['attrs',]


class PreferenceInline(admin.TabularInline):
    model = m.Preference
    fields = ['group', 'key', 'val']
    extra = 1


@admin.register(User)
class UserAdminPlus(UserAdmin):
    inlines = [ProfileInline, PreferenceInline]

