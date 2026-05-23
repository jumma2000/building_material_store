from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Supplier


class SupplierListView(LoginRequiredMixin, ListView):
    """عرض قائمة الموردين"""
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """إضافة مورد جديد"""
    model = Supplier
    fields = ['name', 'phone', 'email', 'address', 'category', 'is_active']
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list')
    success_message = "تم إضافة المورد <b>%(name)s</b> بنجاح"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'إضافة مورد جديد'
        context['button_text'] = 'حفظ'
        return context


class SupplierUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """تعديل بيانات مورد"""
    model = Supplier
    fields = ['name', 'phone', 'email', 'address', 'category', 'is_active']
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list')
    success_message = "تم تعديل بيانات المورد <b>%(name)s</b> بنجاح"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل بيانات المورد'
        context['button_text'] = 'تحديث'
        return context


class SupplierDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """حذف مورد"""
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')
    success_message = "تم حذف المورد بنجاح"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class SupplierDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل مورد"""
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # جلب آخر 10 فواتير شراء لهذا المورد
        context['recent_invoices'] = self.object.invoices.all().order_by('-invoice_date')[:10]
        return context