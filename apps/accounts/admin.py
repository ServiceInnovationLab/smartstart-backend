from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from . import models as m

admin.site.unregister(User)

class UserProfileInline(admin.TabularInline):
    model = m.Profile
    fields = ['attrs',]


@admin.register(User)
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]
