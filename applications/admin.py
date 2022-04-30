from django.contrib import admin

from applications.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "aim")
    readonly_fields = ('user', 'deck_templates_count', 'decks_count')

    filter_horizontal = ()

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
