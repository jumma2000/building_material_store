from django.urls import path
from . import views

app_name = 'warehouses'

urlpatterns = [
    path('', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('add/', views.WarehouseCreateView.as_view(), name='warehouse_add'),
    path('<int:pk>/edit/', views.WarehouseUpdateView.as_view(), name='warehouse_edit'),
    path('<int:pk>/delete/', views.WarehouseDeleteView.as_view(), name='warehouse_delete'),
]