from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from .models import SaleInvoice, SaleDetail
from customers.models import Customer
from warehouses.models import Warehouse
from products.models import Product, StockMovement


class SaleInvoiceListView(LoginRequiredMixin, ListView):
    """عرض قائمة فواتير البيع"""
    model = SaleInvoice
    template_name = 'sales/sale_list.html'
    context_object_name = 'invoices'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(customer__phone__icontains=search)
            )
        return queryset.order_by('-invoice_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class SaleInvoiceDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل فاتورة البيع"""
    model = SaleInvoice
    template_name = 'sales/sale_detail.html'
    context_object_name = 'invoice'


class SaleInvoiceCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """إضافة فاتورة بيع جديدة (من نقطة البيع)"""
    model = SaleInvoice
    fields = [
        'customer', 'warehouse', 'payment_method', 'paid_amount',
        'discount', 'tax', 'shipping', 'notes'
    ]
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:sale_list')
    success_message = "تم إضافة الفاتورة <b>%(invoice_number)s</b> بنجاح"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'فاتورة بيع جديدة'
        context['button_text'] = 'حفظ الفاتورة'
        context['customers'] = Customer.objects.all()
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        context['products'] = Product.objects.filter(is_active=True)
        # جلب السلة من الجلسة (إذا كانت موجودة من واجهة POS)
        cart = self.request.session.get('sale_cart', {})
        context['cart'] = cart
        # حساب المجموع
        subtotal = Decimal('0.00')
        for item in cart.values():
            subtotal += Decimal(str(item['price'])) * Decimal(str(item['quantity']))
        context['subtotal'] = subtotal
        context['total'] = subtotal  # سيتم حسابه بعد الخصم والضريبة والشحن
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # جلب السلة
            cart = request.session.get('sale_cart', {})
            if not cart:
                messages.error(request, 'السلة فارغة')
                return redirect('sales:sale_add')

            # إنشاء رقم فاتورة جديد
            last_invoice = SaleInvoice.objects.order_by('-id').first()
            if last_invoice:
                last_num = int(last_invoice.invoice_number.split('-')[-1]) if '-' in last_invoice.invoice_number else 0
                invoice_number = f"INV-{last_num + 1:05d}"
            else:
                invoice_number = "INV-00001"

            # حساب الإجماليات
            subtotal = Decimal('0.00')
            for item in cart.values():
                subtotal += Decimal(str(item['price'])) * Decimal(str(item['quantity']))

            discount = Decimal(request.POST.get('discount', '0')) or Decimal('0')
            tax = Decimal(request.POST.get('tax', '0')) or Decimal('0')
            shipping = Decimal(request.POST.get('shipping', '0')) or Decimal('0')
            paid_amount = Decimal(request.POST.get('paid_amount', '0')) or Decimal('0')
            payment_method = request.POST.get('payment_method', 'cash')
            customer_id = request.POST.get('customer')
            warehouse_id = request.POST.get('warehouse')
            notes = request.POST.get('notes', '')

            total = subtotal - discount + tax + shipping
            change_amount = paid_amount - total if paid_amount > total else Decimal('0')

            # إنشاء الفاتورة
            invoice = SaleInvoice.objects.create(
                invoice_number=invoice_number,
                customer_id=customer_id if customer_id else None,
                warehouse_id=warehouse_id,
                user=request.user,
                subtotal=subtotal,
                discount=discount,
                tax=tax,
                shipping=shipping,
                total=total,
                payment_method=payment_method,
                paid_amount=paid_amount,
                change_amount=change_amount,
                status='completed',
                notes=notes
            )

            # إنشاء تفاصيل الفاتورة وتحديث المخزون
            for product_id, item in cart.items():
                product = get_object_or_404(Product, id=product_id)
                quantity = Decimal(str(item['quantity']))
                price = Decimal(str(item['price']))

                SaleDetail.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=quantity,
                    price=price,
                    total=quantity * price
                )

                # تحديث المخزون
                product.current_quantity -= quantity
                product.save()

                # تسجيل حركة المخزون
                StockMovement.objects.create(
                    product=product,
                    warehouse_id=warehouse_id,
                    movement_type='out',
                    quantity=quantity,
                    reference_type='sale',
                    reference_id=invoice.id,
                    price_at_movement=price,
                    notes=f'فاتورة بيع رقم {invoice.invoice_number}',
                    created_by=request.user.username
                )

            # تحديث إجمالي مشتريات العميل (اختياري)
            if customer_id:
                customer = Customer.objects.get(id=customer_id)
                customer.total_purchases += total
                customer.total_invoices += 1
                customer.save()

            # تفريغ السلة من الجلسة
            request.session['sale_cart'] = {}
            request.session.modified = True

            messages.success(request, self.success_message % {'invoice_number': invoice.invoice_number})
            return redirect('sales:sale_detail', pk=invoice.pk)

        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
            return redirect('sales:sale_add')


class SaleInvoiceUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """تعديل فاتورة بيع (نادر الاستخدام)"""
    model = SaleInvoice
    fields = ['customer', 'warehouse', 'payment_method', 'paid_amount', 'discount', 'tax', 'shipping', 'notes']
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:sale_list')
    success_message = "تم تعديل الفاتورة <b>%(invoice_number)s</b> بنجاح"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل فاتورة بيع'
        context['button_text'] = 'تحديث الفاتورة'
        context['customers'] = Customer.objects.all()
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        context['products'] = Product.objects.filter(is_active=True)
        context['details'] = self.get_object().details.all()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            invoice = self.get_object()
            # حذف التفاصيل القديمة وإعادة المخزون
            for detail in invoice.details.all():
                product = detail.product
                product.current_quantity += detail.quantity  # نعيد الكمية للمخزون
                product.save()
            invoice.details.all().delete()

            # حفظ الفاتورة بعد التعديل
            response = super().post(request, *args, **kwargs)

            # جلب المنتجات من POST (نفس طريقة الإضافة)
            product_ids = request.POST.getlist('product_id[]')
            quantities = request.POST.getlist('quantity[]')
            prices = request.POST.getlist('price[]')

            for i in range(len(product_ids)):
                if product_ids[i] and quantities[i]:
                    product = get_object_or_404(Product, id=product_ids[i])
                    quantity = Decimal(quantities[i])
                    price = Decimal(prices[i]) if prices[i] else 0

                    SaleDetail.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=quantity,
                        price=price,
                        total=quantity * price
                    )

                    # تحديث المخزون (نقص)
                    product.current_quantity -= quantity
                    product.save()

            messages.success(request, self.success_message % {'invoice_number': invoice.invoice_number})
            return response
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
            return redirect('sales:sale_edit', pk=invoice.pk)


class SaleInvoiceDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """حذف فاتورة بيع"""
    model = SaleInvoice
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sales:sale_list')
    success_message = "تم حذف الفاتورة بنجاح"

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            invoice = self.get_object()
            # إعادة الكميات إلى المخزون
            for detail in invoice.details.all():
                product = detail.product
                product.current_quantity += detail.quantity
                product.save()
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء الحذف: {str(e)}')
            return redirect('sales:sale_list')
        
# ========== دوال API للسلة والباركود ==========

def add_to_cart(request):
    """إضافة منتج إلى السلة (جلسة المستخدم)"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # التحقق من الكمية المتوفرة
        if product.current_quantity < quantity:
            return JsonResponse({
                'status': 'error',
                'message': f'الكمية المتوفرة {product.current_quantity} فقط'
            })
        
        cart = request.session.get('sale_cart', {})
        
        if product_id in cart:
            new_quantity = cart[product_id]['quantity'] + quantity
            if product.current_quantity < new_quantity:
                return JsonResponse({
                    'status': 'error',
                    'message': f'الكمية المتوفرة {product.current_quantity} فقط'
                })
            cart[product_id]['quantity'] = new_quantity
        else:
            cart[product_id] = {
                'name': product.name,
                'price': str(product.sale_price),
                'quantity': quantity,
                'unit': product.get_unit_display(),
                'stock': float(product.current_quantity)
            }
        
        request.session['sale_cart'] = cart
        request.session.modified = True
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'طلب غير صحيح'})


def remove_from_cart(request):
    """حذف منتج من السلة"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        cart = request.session.get('sale_cart', {})
        
        if product_id in cart:
            del cart[product_id]
        
        request.session['sale_cart'] = cart
        request.session.modified = True
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'طلب غير صحيح'})


def update_cart(request):
    """تحديث كمية منتج في السلة"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('sale_cart', {})
        
        if product_id in cart:
            if quantity <= 0:
                del cart[product_id]
            else:
                if product.current_quantity < quantity:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'الكمية المتوفرة {product.current_quantity} فقط'
                    })
                cart[product_id]['quantity'] = quantity
        
        request.session['sale_cart'] = cart
        request.session.modified = True
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'طلب غير صحيح'})


def get_product_by_barcode(request, barcode):
    """البحث عن منتج بالباركود وإرجاع بياناته بصيغة JSON"""
    try:
        product = Product.objects.get(barcode=barcode, is_active=True)
        data = {
            'id': product.id,
            'name': product.name,
            'price': str(product.sale_price),
            'unit': product.get_unit_display(),
            'stock': float(product.current_quantity)
        }
        return JsonResponse({'status': 'success', 'product': data})
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'المنتج غير موجود'})