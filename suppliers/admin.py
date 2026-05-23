from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """إدارة الموردين من لوحة التحكم"""
    list_display = [
        'id', 'name', 'phone', 'category', 'is_active', 'created_at'
    ]
    list_display_links = ['id', 'name']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'phone', 'email', 'address']
    list_editable = ['is_active']
    ordering = ['name']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'phone', 'email', 'address', 'category')
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('تواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )