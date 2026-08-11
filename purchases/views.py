from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from .models import PurchaseInvoice, PurchaseDetail
from suppliers.models import Supplier
from warehouses.models import Warehouse
from products.models import Product, StockMovement


class PurchaseInvoiceListView(LoginRequiredMixin, ListView):
    """عرض قائمة فواتير الشراء"""
    model = PurchaseInvoice
    template_name = 'purchases/purchase_list.html'
    context_object_name = 'invoices'
    paginate_by = 10

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            search = self.request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(
                    Q(invoice_number__icontains=search) |
                    Q(supplier__name__icontains=search) |
                    Q(supplier_bill_number__icontains=search)
                )
            return queryset.order_by('-invoice_date')
        except Exception as e:
            messages.error(self.request, "حدث خطأ أثناء جلب أو بحث فواتير الشراء.")
            return PurchaseInvoice.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['search'] = self.request.GET.get('search', '')
        except Exception:
            context['search'] = ''
        return context


class PurchaseInvoiceDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل فاتورة شراء"""
    model = PurchaseInvoice
    template_name = 'purchases/purchase_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['total'] = self.object.get_total() if hasattr(self.object, 'get_total') else Decimal('0.00')
        except Exception:
            context['total'] = Decimal('0.00')
        return context


class PurchaseInvoiceCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """إضافة فاتورة شراء جديدة"""
    model = PurchaseInvoice
    fields = [
        'invoice_number', 'invoice_date', 'supplier', 'warehouse',
        'supplier_invoice_date', 'supplier_bill_number', 'statement',
        'reference_number', 'notes'
    ]
    template_name = 'purchases/purchase_form.html'
    success_url = reverse_lazy('purchases:purchase_list')
    success_message = "تم إضافة الفاتورة <b>%(invoice_number)s</b> بنجاح"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['title'] = 'إضافة فاتورة شراء جديدة'
            context['button_text'] = 'حفظ الفاتورة'
            context['suppliers'] = Supplier.objects.filter(is_active=True)
            context['warehouses'] = Warehouse.objects.filter(is_active=True)
            context['products'] = Product.objects.filter(is_active=True)
        except Exception:
            context['suppliers'] = []
            context['warehouses'] = []
            context['products'] = []
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()
            if form.is_valid():
                response = super().form_valid(form)

                # حفظ تفاصيل الفاتورة
                product_ids = request.POST.getlist('product_id[]')
                quantities = request.POST.getlist('quantity[]')
                purchase_prices = request.POST.getlist('purchase_price[]')
                sale_prices = request.POST.getlist('sale_price[]')
                expiry_dates = request.POST.getlist('expiry_date[]')
                discounts = request.POST.getlist('discount[]')

                for i in range(len(product_ids)):
                    if product_ids[i] and quantities[i]:
                        product = get_object_or_404(Product, id=product_ids[i])
                        try:
                            quantity = Decimal(quantities[i])
                            p_price = Decimal(purchase_prices[i]) if purchase_prices[i] else Decimal('0')
                            s_price = Decimal(sale_prices[i]) if sale_prices[i] else Decimal('0')
                            disc = Decimal(discounts[i]) if discounts[i] else Decimal('0')
                        except (InvalidOperation, ValueError):
                            raise ValidationError("توجد قيمة رقمية غير صالحة في تفاصيل المنتجات.")

                        expiry = expiry_dates[i] if expiry_dates[i] else None

                        PurchaseDetail.objects.create(
                            invoice=self.object,
                            product=product,
                            quantity=quantity,
                            purchase_price=p_price,
                            sale_price=s_price,
                            expiry_date=expiry,
                            discount=disc
                        )

                        # تحديث المخزون
                        product.current_quantity += quantity
                        product.purchase_price = p_price if p_price > 0 else product.purchase_price
                        product.save()

                        # تسجيل حركة المخزون
                        StockMovement.objects.create(
                            product=product,
                            warehouse=self.object.warehouse,
                            movement_type='in',
                            quantity=quantity,
                            reference_type='purchase',
                            reference_id=self.object.id,
                            expiry_date=expiry,
                            price_at_movement=p_price,
                            notes=f'فاتورة شراء رقم {self.object.invoice_number}',
                            created_by=request.user.username if request.user and request.user.is_authenticated else 'admin'
                        )

                messages.success(request, self.success_message % {'invoice_number': self.object.invoice_number})
                return response
            return self.form_invalid(form)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ الفاتورة: {str(e)}')
            return redirect('purchases:purchase_add')


class PurchaseInvoiceUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """تعديل فاتورة شراء"""
    model = PurchaseInvoice
    fields = [
        'invoice_number', 'invoice_date', 'supplier', 'warehouse',
        'supplier_invoice_date', 'supplier_bill_number', 'statement',
        'reference_number', 'notes'
    ]
    template_name = 'purchases/purchase_form.html'
    success_url = reverse_lazy('purchases:purchase_list')
    success_message = "تم تعديل الفاتورة <b>%(invoice_number)s</b> بنجاح"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['title'] = 'تعديل فاتورة شراء'
            context['button_text'] = 'تحديث الفاتورة'
            context['suppliers'] = Supplier.objects.filter(is_active=True)
            context['warehouses'] = Warehouse.objects.filter(is_active=True)
            context['products'] = Product.objects.filter(is_active=True)
            context['details'] = self.get_object().details.all()
        except Exception:
            context['suppliers'] = []
            context['warehouses'] = []
            context['products'] = []
            context['details'] = []
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            invoice = self.get_object()

            # حذف التفاصيل القديمة وتحديث المخزون (نقص)
            for detail in invoice.details.all():
                product = detail.product
                product.current_quantity -= detail.quantity
                product.save()

            invoice.details.all().delete()

            # حفظ الفاتورة (بعد التعديل)
            response = super().post(request, *args, **kwargs)

            # حفظ التفاصيل الجديدة
            product_ids = request.POST.getlist('product_id[]')
            quantities = request.POST.getlist('quantity[]')
            purchase_prices = request.POST.getlist('purchase_price[]')
            sale_prices = request.POST.getlist('sale_price[]')
            expiry_dates = request.POST.getlist('expiry_date[]')
            discounts = request.POST.getlist('discount[]')

            for i in range(len(product_ids)):
                if product_ids[i] and quantities[i]:
                    product = get_object_or_404(Product, id=product_ids[i])
                    try:
                        quantity = Decimal(quantities[i])
                        p_price = Decimal(purchase_prices[i]) if purchase_prices[i] else Decimal('0')
                        s_price = Decimal(sale_prices[i]) if sale_prices[i] else Decimal('0')
                        disc = Decimal(discounts[i]) if discounts[i] else Decimal('0')
                    except (InvalidOperation, ValueError):
                        continue

                    expiry = expiry_dates[i] if expiry_dates[i] else None

                    PurchaseDetail.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=quantity,
                        purchase_price=p_price,
                        sale_price=s_price,
                        expiry_date=expiry,
                        discount=disc
                    )

                    # تحديث المخزون (زيادة)
                    product.current_quantity += quantity
                    product.save()

            messages.success(request, self.success_message % {'invoice_number': invoice.invoice_number})
            return response
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء التعديل: {str(e)}')
            return redirect('purchases:purchase_edit', pk=self.get_object().pk)


class PurchaseInvoiceDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """حذف فاتورة شراء"""
    model = PurchaseInvoice
    template_name = 'purchases/purchase_confirm_delete.html'
    success_url = reverse_lazy('purchases:purchase_list')
    success_message = "تم حذف الفاتورة بنجاح"

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            invoice = self.get_object()
            # إعادة الكميات (نقص) لأن الحذف يعكس عملية الشراء
            for detail in invoice.details.all():
                product = detail.product
                product.current_quantity -= detail.quantity
                product.save()
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء الحذف: {str(e)}')
            return redirect('purchases:purchase_list')