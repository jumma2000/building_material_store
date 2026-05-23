from django.db import models
from decimal import Decimal


class Customer(models.Model):
    """نموذج العميل - يدعم الأفراد وشركات المقاولات والمحلات"""
    
    name = models.CharField(max_length=200, verbose_name="اسم العميل")
    phone = models.CharField(max_length=20, unique=True, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    address = models.CharField(max_length=300, blank=True, null=True, verbose_name="العنوان")
    
    # نوع العميل (حقل جديد لمواد البناء)
    CUSTOMER_TYPES = [
        ('individual', 'فرد'),
        ('company', 'شركة مقاولات'),
        ('store', 'متجر'),
    ]
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='individual', verbose_name="نوع العميل")
    
    # إحصائيات تلقائية
    total_purchases = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="إجمالي المشتريات"
    )
    total_invoices = models.IntegerField(default=0, verbose_name="عدد الفواتير")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    def __str__(self):
        return f"{self.name} ({self.get_customer_type_display()}) - {self.phone}"
    
    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"
        ordering = ['name']