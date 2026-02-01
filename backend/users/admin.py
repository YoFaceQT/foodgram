from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'username', 'first_name', 'last_name', 'email',)
    search_fields = ('email', 'username',)
    list_filter = ('email', 'username',)
