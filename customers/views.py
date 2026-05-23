from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Customer


class CustomerListView(LoginRequiredMixin, ListView):
    """عرض قائمة العملاء"""
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
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


class CustomerCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """إضافة عميل جديد"""
    model = Customer
    fields = ['name', 'phone', 'email', 'address', 'customer_type']
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')
    success_message = "تم إضافة العميل <b>%(name)s</b> بنجاح"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'إضافة عميل جديد'
        context['button_text'] = 'حفظ'
        return context


class CustomerUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """تعديل بيانات عميل"""
    model = Customer
    fields = ['name', 'phone', 'email', 'address', 'customer_type']
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')
    success_message = "تم تعديل بيانات العميل <b>%(name)s</b> بنجاح"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل بيانات العميل'
        context['button_text'] = 'تحديث'
        return context


class CustomerDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """حذف عميل"""
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')
    success_message = "تم حذف العميل بنجاح"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class CustomerDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل عميل"""
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # جلب آخر 10 فواتير للعميل
        context['recent_invoices'] = self.object.invoices.all().order_by('-invoice_date')[:10]
        return context