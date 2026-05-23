from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # قائمة العملاء
    path('', views.CustomerListView.as_view(), name='customer_list'),
    
    # إضافة عميل
    path('add/', views.CustomerCreateView.as_view(), name='customer_add'),
    
    # تفاصيل عميل
    path('<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    
    # تعديل عميل
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    
    # حذف عميل
    path('<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
]