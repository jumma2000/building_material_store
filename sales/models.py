from django.db import models
from decimal import Decimal
from customers.models import Customer
from warehouses.models import Warehouse
from products.models import Product
from django.contrib.auth.models import User


class SaleInvoice(models.Model):
    """نموذج فاتورة البيع - بيع مواد البناء للعملاء"""
    
    PAYMENT_METHODS = [
        ('cash', 'نقدي'),
        ('card', 'بطاقة'),
        ('credit', 'آجل'),
    ]
    
    INVOICE_STATUS = [
        ('draft', 'مسودة'),
        ('completed', 'مكتملة'),
        ('cancelled', 'ملغاة'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الفاتورة")
    invoice_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الفاتورة")
    
    # العلاقات
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices', verbose_name="العميل", null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='sale_invoices', verbose_name="المخزن")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sale_invoices', verbose_name="المستخدم")
    
    # الحسابات
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المجموع الفرعي")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الخصم")
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الضريبة")
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الشحن")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الإجمالي")
    
    # الدفع
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash', verbose_name="طريقة الدفع")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المدفوع")
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الباقي")
    
    # الحالة
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='completed', verbose_name="الحالة")
    notes = models.CharField(max_length=500, blank=True, null=True, verbose_name="ملاحظات")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    
    def __str__(self):
        return f"فاتورة {self.invoice_number} - {self.total} د.ل"
    
    class Meta:
        verbose_name = "فاتورة بيع"
        verbose_name_plural = "فواتير البيع"
        ordering = ['-invoice_date']


class SaleDetail(models.Model):
    """تفاصيل فاتورة البيع - المنتجات المباعة"""
    
    invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE, related_name='details', verbose_name="الفاتورة")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_details', verbose_name="المنتج")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكمية")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الخصم")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الإجمالي")
    
    def save(self, *args, **kwargs):
        self.total = (self.quantity * self.price) - self.discount
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    class Meta:
        verbose_name = "تفاصيل البيع"
        verbose_name_plural = "تفاصيل البيع"