from django.db import models


class Category(models.Model):
    """نموذج التصنيف - لتصنيف منتجات مواد البناء"""
    
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name="الوصف")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"
        ordering = ['name']


class Product(models.Model):
    """نموذج المنتج - خاص بمواد البناء"""
    
    # وحدات القياس الخاصة بمواد البناء
    UNIT_CHOICES = [
        ('bag', 'كيس'),
        ('piece', 'قطعة'),
        ('meter', 'متر'),
        ('square_meter', 'متر مربع'),
        ('ton', 'طن'),
        ('kg', 'كيلوجرام'),
        ('barrel', 'برميل'),
        ('gallon', 'جالون'),
        ('box', 'كرتونة'),
        ('roll', 'لفة'),
        ('sheet', 'لوح'),
        ('liter', 'لتر'),
    ]
    
    # المعلومات الأساسية
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="الباركود")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name="التصنيف")
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.PROTECT, related_name='products', verbose_name="المخزن")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece', verbose_name="وحدة القياس")
    
    # الأسعار
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="سعر الشراء")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="سعر البيع")
    
    # الكميات
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الكمية الحالية")
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الحد الأدنى للتنبيه")
    
    # حقول خاصة بمواد البناء
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="الوزن (كجم)")
    length_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="الطول (متر)")
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name="اللون")
    manufacturer = models.CharField(max_length=200, blank=True, null=True, verbose_name="الشركة المصنعة")
    
    # الصلاحية (معظم مواد البناء ليس لها صلاحية، لكن نترك الخيار)
    has_expiry = models.BooleanField(default=False, verbose_name="له تاريخ انتهاء")
    expiry_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الانتهاء")
    
    # معلومات إضافية
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="صورة المنتج")
    is_active = models.BooleanField(default=True, verbose_name="مفعل")
    notes = models.CharField(max_length=500, blank=True, null=True, verbose_name="ملاحظات")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    def __str__(self):
        return f"{self.name} - {self.get_unit_display()}"
    
    def is_low_stock(self):
        """التحقق إذا كان المخزون منخفض"""
        return self.current_quantity <= self.min_quantity
    
    def get_profit_margin(self):
        """حساب هامش الربح"""
        if self.purchase_price > 0:
            return ((self.sale_price - self.purchase_price) / self.purchase_price) * 100
        return 0
    
    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        ordering = ['category', 'name']

class StockMovement(models.Model):
    """نموذج حركة المخزون - لتسجيل كل حركة دخول وخروج للمنتجات"""
    
    MOVEMENT_TYPES = [
        ('in', 'داخل (شراء)'),
        ('out', 'خارج (بيع)'),
        ('return_in', 'مرتجع داخل'),
        ('return_out', 'مرتجع خارج'),
        ('adjustment', 'تسوية مخزون'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='movements', verbose_name="المنتج")
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.PROTECT, related_name='movements', verbose_name="المخزن")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, verbose_name="نوع الحركة")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكمية")
    
    # مرجع الحركة (فاتورة شراء أو بيع)
    reference_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="نوع المرجع")
    reference_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="رقم المرجع")
    
    # معلومات إضافية خاصة بمواد البناء
    expiry_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الانتهاء")
    price_at_movement = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="السعر وقت الحركة")
    notes = models.CharField(max_length=500, blank=True, null=True, verbose_name="ملاحظات")
    created_by = models.CharField(max_length=150, blank=True, null=True, verbose_name="تم بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الحركة")
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} - {self.quantity}"
    
    class Meta:
        verbose_name = "حركة مخزون"
        verbose_name_plural = "حركات المخزون"
        ordering = ['-created_at']