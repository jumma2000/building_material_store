from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from .models import Warehouse


class WarehouseListView(LoginRequiredMixin, ListView):
    """عرض قائمة المخازن"""
    model = Warehouse
    template_name = 'warehouses/warehouse_list.html'
    context_object_name = 'warehouses'
    paginate_by = 10
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            search = self.request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(location__icontains=search)
                )
            return queryset.order_by('id')
        except Exception as e:
            messages.error(self.request, "حدث خطأ أثناء جلب أو بحث المخازن.")
            return Warehouse.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['search'] = self.request.GET.get('search', '')
        except Exception:
            context['search'] = ''
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
        try:
            context['title'] = 'إضافة مخزن جديد'
            context['button_text'] = 'حفظ'
        except Exception:
            pass
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'حدث خطأ أثناء حفظ المخزن: {str(e)}')
            return redirect('warehouses:warehouse_add')


class WarehouseUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """تعديل بيانات مخزن"""
    model = Warehouse
    fields = ['name', 'location', 'is_active']
    template_name = 'warehouses/warehouse_form.html'
    success_url = reverse_lazy('warehouses:warehouse_list')
    success_message = "تم تعديل بيانات المخزن <b>%(name)s</b> بنجاح"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['title'] = 'تعديل بيانات المخزن'
            context['button_text'] = 'تحديث'
        except Exception:
            pass
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'حدث خطأ أثناء تعديل المخزن: {str(e)}')
            return redirect('warehouses:warehouse_edit', pk=self.get_object().pk)


class WarehouseDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """حذف مخزن"""
    model = Warehouse
    template_name = 'warehouses/warehouse_confirm_delete.html'
    success_url = reverse_lazy('warehouses:warehouse_list')
    success_message = "تم حذف المخزن بنجاح"
    
    def delete(self, request, *args, **kwargs):
        try:
            messages.success(self.request, self.success_message)
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف المخزن (قد يكون مرتبطاً ببيانات أخرى): {str(e)}')
            return redirect('warehouses:warehouse_list')
        