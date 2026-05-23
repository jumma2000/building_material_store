from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    # قائمة الموردين
    path('', views.SupplierListView.as_view(), name='supplier_list'),
    
    # إضافة مورد
    path('add/', views.SupplierCreateView.as_view(), name='supplier_add'),
    
    # تفاصيل مورد
    path('<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    
    # تعديل مورد
    path('<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    
    # حذف مورد
    path('<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
]