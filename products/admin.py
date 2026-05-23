from django.contrib import admin
from .models import Category, Product, StockMovement


class StockMovementInline(admin.TabularInline):
    """عرض حركات المخزون داخل صفحة المنتج"""
    model = StockMovement
    extra = 0  # لا تظهر حقول فارغة إضافية
    fields = ['movement_type', 'quantity', 'price_at_movement', 'reference_type', 'reference_id', 'created_at']
    readonly_fields = ['created_at']
    can_delete = False
    show_change_link = True
    classes = ['collapse']  # قابلة للطي


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """إدارة التصنيفات من لوحة التحكم"""
    list_display = ['id', 'name', 'description']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """إدارة المنتجات من لوحة التحكم"""
    list_display = [
        'id', 'name', 'barcode', 'category', 'warehouse', 'unit',
        'sale_price', 'current_quantity', 'is_low_stock', 'is_active'
    ]
    list_display_links = ['id', 'name']
    list_filter = ['category', 'warehouse', 'is_active', 'unit', 'has_expiry']
    search_fields = ['name', 'barcode', 'manufacturer']
    list_editable = ['sale_price', 'is_active']
    readonly_fields = ['current_quantity', 'created_at', 'updated_at']
    inlines = [StockMovementInline]
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'barcode', 'category', 'warehouse', 'unit')
        }),
        ('الأسعار', {
            'fields': ('purchase_price', 'sale_price')
        }),
        ('المخزون', {
            'fields': ('current_quantity', 'min_quantity')
        }),
        ('خصائص إضافية (مواد بناء)', {
            'fields': ('weight_kg', 'length_m', 'color', 'manufacturer'),
            'classes': ('collapse',)
        }),
        ('الصلاحية', {
            'fields': ('has_expiry', 'expiry_date'),
            'classes': ('collapse',)
        }),
        ('إضافات', {
            'fields': ('image', 'is_active', 'notes'),
            'classes': ('collapse',)
        }),
        ('تواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_low_stock(self, obj):
        """حقل محسوب لتوضيح حالة المخزون في القائمة"""
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'مخزون منخفض'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """إدارة حركات المخزون"""
    list_display = [
        'id', 'product', 'movement_type', 'quantity', 
        'reference_type', 'reference_id', 'created_at', 'created_by'
    ]
    list_filter = ['movement_type', 'reference_type', 'created_at']
    search_fields = ['product__name', 'notes', 'created_by']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات الحركة', {
            'fields': ('product', 'warehouse', 'movement_type', 'quantity')
        }),
        ('المرجع', {
            'fields': ('reference_type', 'reference_id')
        }),
        ('تفاصيل إضافية', {
            'fields': ('expiry_date', 'price_at_movement', 'notes', 'created_by')
        }),
        ('تاريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )