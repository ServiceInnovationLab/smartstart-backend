from django.contrib import admin
from . import models as m

class PhaseMetadataAdmin(admin.ModelAdmin):
    exclude = ('modified_by',)
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        obj.save()


admin.site.register(m.PhaseMetadata, PhaseMetadataAdmin)
