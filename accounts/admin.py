from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, OTP

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_email_verified', 'is_staff', 'date_joined')
    list_filter = ('is_email_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'country', 'created_at')
    search_fields = ('user__email', 'full_name', 'nick_name')

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'is_verified', 'created_at', 'expires_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('email', 'code')
