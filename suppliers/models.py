from django.db import models

# Create your models here.
from django.db import models


class Supplier(models.Model):
    """نموذج المورد - شركات توريد مواد البناء"""
    
    name = models.CharField(max_length=200, verbose_name="اسم المورد")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    address = models.CharField(max_length=300, blank=True, null=True, verbose_name="العنوان")
    
    # حقل جديد خاص بمواد البناء: تصنيف المورد (إسمنت، حديد، خشب، دهانات، إلخ)
    SUPPLIER_CATEGORIES = [
        ('cement', 'إسمنت وخرسانة'),
        ('steel', 'حديد وتسليح'),
        ('wood', 'أخشاب'),
        ('paint', 'دهانات'),
        ('ceramic', 'سيراميك وبورسلين'),
        ('plumbing', 'سباكة'),
        ('electrical', 'كهرباء'),
        ('tools', 'أدوات'),
        ('general', 'عام'),
    ]
    category = models.CharField(max_length=20, choices=SUPPLIER_CATEGORIES, default='general', verbose_name="تصنيف المورد")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"
    
    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردين"
        ordering = ['name']