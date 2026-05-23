from django.db import models
from decimal import Decimal
from suppliers.models import Supplier
from warehouses.models import Warehouse


class PurchaseInvoice(models.Model):
    """نموذج فاتورة الشراء - لشراء مواد البناء من الموردين"""
    
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الفاتورة")
    invoice_date = models.DateField(verbose_name="تاريخ الفاتورة")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='invoices', verbose_name="المورد")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='purchase_invoices', verbose_name="المخزن")
    
    # معلومات إضافية
    supplier_invoice_date = models.DateField(blank=True, null=True, verbose_name="تاريخ فاتورة المورد")
    supplier_bill_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم فاتورة المورد")
    statement = models.CharField(max_length=500, blank=True, null=True, verbose_name="البيان")
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="الرقم المرجعي")
    
    notes = models.CharField(max_length=500, blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    def __str__(self):
        return f"فاتورة {self.invoice_number} - {self.supplier.name}"
    
    def get_total(self):
        """حساب إجمالي الفاتورة (سيتم حسابه من التفاصيل)"""
        total = Decimal('0.00')
        for detail in self.details.all():
            total += detail.get_subtotal()
        return total
    
    class Meta:
        verbose_name = "فاتورة شراء"
        verbose_name_plural = "فواتير الشراء"
        ordering = ['-invoice_date']

class PurchaseDetail(models.Model):
    """تفاصيل فاتورة الشراء - المنتجات المشتراة"""
    
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='details', verbose_name="الفاتورة")
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='purchase_details', verbose_name="المنتج")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكمية")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الشراء")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="سعر البيع")
    expiry_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الانتهاء")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="التخفيض")
    
    def __str__(self):
        return f"{self.product.name} - كمية: {self.quantity}"
    
    def get_subtotal(self):
        """حساب إجمالي هذا الصف"""
        return (self.quantity * self.purchase_price) - self.discount
    
    class Meta:
        verbose_name = "تفاصيل الفاتورة"
        verbose_name_plural = "تفاصيل الفواتير"