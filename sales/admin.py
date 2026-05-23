from django.contrib import admin
from .models import SaleInvoice, SaleDetail


class SaleDetailInline(admin.TabularInline):
    """عرض تفاصيل فاتورة البيع داخل صفحة الفاتورة الرئيسية"""
    model = SaleDetail
    extra = 1
    fields = ['product', 'quantity', 'price', 'discount', 'total']
    readonly_fields = ['total']


@admin.register(SaleInvoice)
class SaleInvoiceAdmin(admin.ModelAdmin):
    """إدارة فواتير البيع من لوحة التحكم"""
    list_display = [
        'id', 'invoice_number', 'invoice_date', 'customer', 
        'warehouse', 'total', 'payment_method', 'status'
    ]
    list_display_links = ['id', 'invoice_number']
    list_filter = ['payment_method', 'status', 'invoice_date', 'warehouse']
    search_fields = ['invoice_number', 'customer__name', 'customer__phone']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    inlines = [SaleDetailInline]
    date_hierarchy = 'invoice_date'
    
    fieldsets = (
        ('معلومات الفاتورة', {
            'fields': ('invoice_number', 'invoice_date', 'customer', 'warehouse', 'user')
        }),
        ('الحسابات', {
            'fields': ('subtotal', 'discount', 'tax', 'shipping', 'total')
        }),
        ('الدفع', {
            'fields': ('payment_method', 'paid_amount', 'change_amount')
        }),
        ('الحالة', {
            'fields': ('status', 'notes')
        }),
        ('تواريخ النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    """إدارة تفاصيل فواتير البيع"""
    list_display = ['id', 'invoice', 'product', 'quantity', 'price', 'total']
    list_filter = ['invoice__status', 'invoice__payment_method']
    search_fields = ['product__name', 'invoice__invoice_number']
    readonly_fields = ['total']