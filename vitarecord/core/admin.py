from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, MedicalRecord

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'unique_id', 'role', 'email']
    list_filter  = ['role']
    fieldsets    = UserAdmin.fieldsets + (('Medical Info', {'fields': ('role', 'unique_id')}),)

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'diagnosis', 'created_at']
    list_filter  = ['created_at']
    search_fields = ['patient__unique_id', 'patient__username']
