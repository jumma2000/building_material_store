from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Product, Category
from warehouses.models import Warehouse


class ProductListView(LoginRequiredMixin, ListView):
    """عرض قائمة المنتجات"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(barcode__icontains=search)
            )
        
        category_id = self.request.GET.get('category', '')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """إضافة منتج جديد"""
    model = Product
    fields = [
        'name', 'barcode', 'category', 'warehouse', 'unit',
        'purchase_price', 'sale_price', 'current_quantity', 'min_quantity',
        'weight_kg', 'length_m', 'color', 'manufacturer',
        'has_expiry', 'expiry_date', 'image', 'is_active', 'notes'
    ]
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')
    success_message = "تم إضافة المنتج <b>%(name)s</b> بنجاح"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'إضافة منتج جديد'
        context['button_text'] = 'حفظ'
        context['categories'] = Category.objects.all()
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        return context


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """تعديل بيانات منتج"""
    model = Product
    fields = [
        'name', 'barcode', 'category', 'warehouse', 'unit',
        'purchase_price', 'sale_price', 'current_quantity', 'min_quantity',
        'weight_kg', 'length_m', 'color', 'manufacturer',
        'has_expiry', 'expiry_date', 'image', 'is_active', 'notes'
    ]
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')
    success_message = "تم تعديل بيانات المنتج <b>%(name)s</b> بنجاح"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل بيانات المنتج'
        context['button_text'] = 'تحديث'
        context['categories'] = Category.objects.all()
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        return context


class ProductDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """حذف منتج"""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    success_message = "تم حذف المنتج بنجاح"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ProductDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل منتج"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_movements'] = self.object.movements.all().order_by('-created_at')[:10]
        return context