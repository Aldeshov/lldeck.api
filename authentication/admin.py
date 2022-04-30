from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authentication.forms import UserCreationForm
from authentication.models import User

admin.site.site_header = "LLDeck Django administration"


@admin.register(User)
class Admin(UserAdmin):
    # The forms to add and change user instances
    ordering = ("name",)
    list_display = ("name", "email", "phone_number", "is_staff")
    add_form = UserCreationForm
    readonly_fields = ('date_joined', 'profile')
    _fields = ('name', 'email', 'password', 'phone_number', 'date_joined', 'avatar', 'profile', 'is_staff', 'is_active')
    _add_fields = ('name', 'email', 'phone_number', 'password1', 'password2')

    fieldsets = ((None, {'fields': _fields}),)
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': _add_fields}),)

    filter_horizontal = ()
