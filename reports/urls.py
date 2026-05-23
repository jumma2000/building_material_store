from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # لوحة التحكم الرئيسية
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # تقرير المخزون
    path('inventory/', views.InventoryReportView.as_view(), name='inventory_report'),
    
    # تقرير المشتريات
    path('purchases/', views.PurchasesReportView.as_view(), name='purchases_report'),
    
    # تقرير المبيعات
    path('sales/', views.SalesReportView.as_view(), name='sales_report'),
    
    # تقرير الأرباح
    path('profits/', views.ProfitsReportView.as_view(), name='profits_report'),
]