from django.contrib import admin
from .models import Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    """إدارة المخازن من لوحة التحكم"""
    list_display = ['id', 'name', 'location', 'is_active', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'location']
    list_editable = ['is_active']
    readonly_fields = ['created_at']   # ✅ مهم: أضف created_at هنا
    ordering = ['name']
    
    fieldsets = (
        ('معلومات المخزن', {
            'fields': ('name', 'location')
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('تواريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )