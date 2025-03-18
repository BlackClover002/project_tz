from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Task

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "username", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("email",)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task)
