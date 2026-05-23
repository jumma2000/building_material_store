from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Warehouse


class WarehouseListView(LoginRequiredMixin, ListView):
    """عرض قائمة المخازن"""
    model = Warehouse
    template_name = 'warehouses/warehouse_list.html'
    context_object_name = 'warehouses'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class WarehouseCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """إضافة مخزن جديد"""
    model = Warehouse
    fields = ['name', 'location', 'is_active']
    template_name = 'warehouses/warehouse_form.html'
    success_url = reverse_lazy('warehouses:warehouse_list')
    success_message = "تم إضافة المخزن <b>%(name)s</b> بنجاح"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'إضافة مخزن جديد'
        context['button_text'] = 'حفظ'
        return context


class WarehouseUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """تعديل بيانات مخزن"""
    model = Warehouse
    fields = ['name', 'location', 'is_active']
    template_name = 'warehouses/warehouse_form.html'
    success_url = reverse_lazy('warehouses:warehouse_list')
    success_message = "تم تعديل بيانات المخزن <b>%(name)s</b> بنجاح"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل بيانات المخزن'
        context['button_text'] = 'تحديث'
        return context


class WarehouseDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """حذف مخزن"""
    model = Warehouse
    template_name = 'warehouses/warehouse_confirm_delete.html'
    success_url = reverse_lazy('warehouses:warehouse_list')
    success_message = "تم حذف المخزن بنجاح"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)