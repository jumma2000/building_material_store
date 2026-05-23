from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # قائمة فواتير البيع
    path('', views.SaleInvoiceListView.as_view(), name='sale_list'),
    
    # إضافة فاتورة بيع (شاشة البيع)
    path('add/', views.SaleInvoiceCreateView.as_view(), name='sale_add'),
    
    # تفاصيل فاتورة بيع
    path('<int:pk>/', views.SaleInvoiceDetailView.as_view(), name='sale_detail'),
    
    # تعديل فاتورة بيع
    path('<int:pk>/edit/', views.SaleInvoiceUpdateView.as_view(), name='sale_edit'),
    
    # حذف فاتورة بيع
    path('<int:pk>/delete/', views.SaleInvoiceDeleteView.as_view(), name='sale_delete'),
    
    # API: إضافة منتج إلى السلة (لشاشة البيع)
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    
    # API: حذف منتج من السلة
    path('api/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    
    # API: تحديث كمية منتج في السلة
    path('api/update-cart/', views.update_cart, name='update_cart'),
    
    # API: البحث عن منتج بالباركود
    path('api/get-product/<str:barcode>/', views.get_product_by_barcode, name='get_product_by_barcode'),
]