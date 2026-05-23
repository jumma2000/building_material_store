from django.db import models


class Warehouse(models.Model):
    """نموذج المخزن - لتخزين مواد البناء"""
    
    name = models.CharField(max_length=100, verbose_name="اسم المخزن")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="الموقع")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "مخزن"
        verbose_name_plural = "المخازن"
        ordering = ['name']