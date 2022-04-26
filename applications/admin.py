from django.contrib import admin

from applications.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    readonly_fields = ('user',)

    filter_horizontal = ()

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.register(Profile, ProfileAdmin)
