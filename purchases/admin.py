from django.contrib import admin
from .models import PurchaseInvoice, PurchaseDetail


class PurchaseDetailInline(admin.TabularInline):
    """عرض تفاصيل الفاتورة داخل صفحة الفاتورة الرئيسية"""
    model = PurchaseDetail
    extra = 1
    fields = ['product', 'quantity', 'purchase_price', 'sale_price', 'expiry_date', 'discount', 'get_subtotal']
    readonly_fields = ['get_subtotal']
    
    def get_subtotal(self, obj):
        if obj.id:
            return obj.get_subtotal()
        return 0
    get_subtotal.short_description = 'المجموع'


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    """إدارة فواتير الشراء من لوحة التحكم"""
    list_display = [
        'id', 'invoice_number', 'invoice_date', 'supplier', 
        'warehouse', 'get_total', 'created_at'
    ]
    list_display_links = ['id', 'invoice_number']
    list_filter = ['invoice_date', 'supplier', 'warehouse', 'created_at']
    search_fields = ['invoice_number', 'supplier__name', 'supplier_bill_number', 'reference_number']
    readonly_fields = ['created_at']
    inlines = [PurchaseDetailInline]
    date_hierarchy = 'invoice_date'
    
    fieldsets = (
        ('معلومات الفاتورة الأساسية', {
            'fields': ('invoice_number', 'invoice_date', 'supplier', 'warehouse')
        }),
        ('معلومات إضافية من المورد', {
            'fields': ('supplier_invoice_date', 'supplier_bill_number', 'statement', 'reference_number', 'notes'),
            'classes': ('collapse',)
        }),
        ('تواريخ النظام', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'الإجمالي'


@admin.register(PurchaseDetail)
class PurchaseDetailAdmin(admin.ModelAdmin):
    """إدارة تفاصيل فواتير الشراء"""
    list_display = ['id', 'invoice', 'product', 'quantity', 'purchase_price', 'get_subtotal']
    list_filter = ['invoice__supplier', 'product__category']
    search_fields = ['product__name', 'invoice__invoice_number']
    readonly_fields = ['get_subtotal']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'المجموع'