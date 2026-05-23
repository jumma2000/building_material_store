from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """إدارة العملاء من لوحة التحكم"""
    list_display = [
        'id', 'name', 'phone', 'customer_type', 
        'total_invoices', 'total_purchases', 'created_at'
    ]
    list_display_links = ['id', 'name']
    list_filter = ['customer_type', 'created_at']
    search_fields = ['name', 'phone', 'email', 'address']
    readonly_fields = ['total_purchases', 'total_invoices', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'phone', 'email', 'address', 'customer_type')
        }),
        ('إحصائيات (تلقائية)', {
            'fields': ('total_purchases', 'total_invoices'),
            'classes': ('collapse',)
        }),
        ('تواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )