from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Product, Category
from warehouses.models import Warehouse


class ProductListView(LoginRequiredMixin, ListView):
    """عرض قائمة المنتجات"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            search = self.request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(barcode__icontains=search)
                )
            
            category_id = self.request.GET.get('category', '')
            if category_id:
                # التحقق من أن رقم الفئة رقم صحيح لمنع حدوث استثناء
                try:
                    cat_id_int = int(category_id)
                    queryset = queryset.filter(category_id=cat_id_int)
                except ValueError:
                    pass
            
            return queryset
        except Exception as e:
            messages.error(self.request, "حدث خطأ أثناء تصفية أو بحث المنتجات.")
            return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['search'] = self.request.GET.get('search', '')
            context['categories'] = Category.objects.all()
            context['selected_category'] = self.request.GET.get('category', '')
        except Exception:
            context['categories'] = []
            context['selected_category'] = ''
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
    
    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except (ValidationError, Exception) as e:
            messages.error(self.request, "فشل في حفظ المنتج، تأكد من صحة الأرقام والبيانات المدخلة.")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['title'] = 'إضافة منتج جديد'
            context['button_text'] = 'حفظ'
            context['categories'] = Category.objects.all()
            context['warehouses'] = Warehouse.objects.filter(is_active=True)
        except Exception:
            context['categories'] = []
            context['warehouses'] = []
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
    
    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except (ValidationError, Exception) as e:
            messages.error(self.request, "فشل في تحديث بيانات المنتج، تحقق من القيم المدخلة.")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['title'] = 'تعديل بيانات المنتج'
            context['button_text'] = 'تحديث'
            context['categories'] = Category.objects.all()
            context['warehouses'] = Warehouse.objects.filter(is_active=True)
        except Exception:
            context['categories'] = []
            context['warehouses'] = []
        return context


class ProductDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """حذف منتج"""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    success_message = "تم حذف المنتج بنجاح"
    
    def delete(self, request, *args, **kwargs):
        try:
            messages.success(self.request, self.success_message)
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, "تعسّر حذف المنتج لارتباطه بفواتير أو عمليات بيع وشراء سابقة.")
            return reverse_lazy('products:product_list')


class ProductDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل منتج"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['recent_movements'] = self.object.movements.all().order_by('-created_at')[:10]
        except Exception:
            context['recent_movements'] = []
        return context