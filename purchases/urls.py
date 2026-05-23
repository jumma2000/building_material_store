from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    # قائمة فواتير الشراء
    path('', views.PurchaseInvoiceListView.as_view(), name='purchase_list'),
    
    # إضافة فاتورة شراء
    path('add/', views.PurchaseInvoiceCreateView.as_view(), name='purchase_add'),
    
    # تفاصيل فاتورة شراء
    path('<int:pk>/', views.PurchaseInvoiceDetailView.as_view(), name='purchase_detail'),
    
    # تعديل فاتورة شراء
    path('<int:pk>/edit/', views.PurchaseInvoiceUpdateView.as_view(), name='purchase_edit'),
    
    # حذف فاتورة شراء
    path('<int:pk>/delete/', views.PurchaseInvoiceDeleteView.as_view(), name='purchase_delete'),
]