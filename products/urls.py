from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # قائمة المنتجات
    path('', views.ProductListView.as_view(), name='product_list'),
    
    # إضافة منتج
    path('add/', views.ProductCreateView.as_view(), name='product_add'),
    
    # تفاصيل منتج
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # تعديل منتج
    path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    
    # حذف منتج
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
]