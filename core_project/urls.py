from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('customers/', include('customers.urls')),
    path('suppliers/', include('suppliers.urls')), 
    path('products/', include('products.urls')),
    path('warehouses/', include('warehouses.urls')), 
    path('purchases/', include('purchases.urls')), 
    path('sales/', include('sales.urls')),  # أضف هذا # أضف هذا
    path('reports/', include('reports.urls')),
      
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)