from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, F
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta

from customers.models import Customer
from suppliers.models import Supplier
from warehouses.models import Warehouse
from products.models import Product, Category, StockMovement
from purchases.models import PurchaseInvoice, PurchaseDetail
from sales.models import SaleInvoice, SaleDetail


class DashboardView(LoginRequiredMixin, TemplateView):
    """لوحة التحكم الرئيسية - عرض الإحصائيات العامة"""
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # إحصائيات المنتجات
            context['total_products'] = Product.objects.count()
            context['active_products'] = Product.objects.filter(is_active=True).count()
            context['low_stock_products'] = Product.objects.filter(current_quantity__lte=F('min_quantity')).count()
            context['out_of_stock'] = Product.objects.filter(current_quantity=0).count()
            
            # إحصائيات العملاء والموردين والمخازن
            context['total_customers'] = Customer.objects.count()
            context['total_suppliers'] = Supplier.objects.count()
            context['total_warehouses'] = Warehouse.objects.filter(is_active=True).count()
            
            # إحصائيات المشتريات
            context['total_purchase_invoices'] = PurchaseInvoice.objects.count()
            total_purchases = PurchaseDetail.objects.aggregate(
                total=Sum(F('quantity') * F('purchase_price'))
            )['total'] or Decimal('0.00')
            context['total_purchases'] = total_purchases
            
            # إحصائيات المبيعات
            context['total_sale_invoices'] = SaleInvoice.objects.filter(status='completed').count()
            total_sales = SaleInvoice.objects.filter(status='completed').aggregate(
                total=Sum('total')
            )['total'] or Decimal('0.00')
            context['total_sales'] = total_sales
            
            # حساب الأرباح
            context['total_profit'] = total_sales - total_purchases
            if total_sales > 0:
                context['profit_margin'] = (context['total_profit'] / total_sales) * 100
            else:
                context['profit_margin'] = Decimal('0.00')
            
            # أحدث الفواتير
            context['recent_purchases'] = PurchaseInvoice.objects.all().order_by('-created_at')[:5]
            context['recent_sales'] = SaleInvoice.objects.filter(status='completed').order_by('-created_at')[:5]
            
            # المنتجات منخفضة المخزون
            context['low_stock_list'] = Product.objects.filter(
                current_quantity__lte=F('min_quantity'), 
                is_active=True
            )[:10]
            
            # أفضل المنتجات مبيعاً (حسب الكمية)
            top_products = SaleDetail.objects.values('product__name', 'product__id').annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('total')
            ).order_by('-total_quantity')[:5]
            context['top_products'] = top_products
            
        except Exception as e:
            messages.error(self.request, f"حدث خطأ أثناء تحميل بيانات لوحة التحكم: {str(e)}")
            # تعيين قيم افتراضية لضمان عدم تعطل القالب
            context.update({
                'total_products': 0, 'active_products': 0, 'low_stock_products': 0, 'out_of_stock': 0,
                'total_customers': 0, 'total_suppliers': 0, 'total_warehouses': 0,
                'total_purchase_invoices': 0, 'total_purchases': Decimal('0.00'),
                'total_sale_invoices': 0, 'total_sales': Decimal('0.00'),
                'total_profit': Decimal('0.00'), 'profit_margin': Decimal('0.00'),
                'recent_purchases': [], 'recent_sales': [], 'low_stock_list': [], 'top_products': []
            })
        return context


class InventoryReportView(LoginRequiredMixin, ListView):
    """تقرير المخزون - عرض المنتجات مع الكميات والأسعار"""
    model = Product
    template_name = 'reports/inventory_report.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            
            # فلترة حسب التصنيف
            category_id = self.request.GET.get('category', '').strip()
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            
            # فلترة حسب المخزن
            warehouse_id = self.request.GET.get('warehouse', '').strip()
            if warehouse_id:
                queryset = queryset.filter(warehouse_id=warehouse_id)
            
            # فلترة حسب حالة المخزون
            stock_status = self.request.GET.get('stock_status', '').strip()
            if stock_status == 'low':
                queryset = queryset.filter(current_quantity__lte=F('min_quantity'))
            elif stock_status == 'out':
                queryset = queryset.filter(current_quantity=0)
            
            # بحث
            search = self.request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(barcode__icontains=search)
                )
            
            return queryset.order_by('id')
        except Exception as e:
            messages.error(self.request, "حدث خطأ أثناء جلب تقرير المخزون.")
            return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # بيانات الفلترة
            context['categories'] = Category.objects.all()
            context['warehouses'] = Warehouse.objects.filter(is_active=True)
            context['selected_category'] = self.request.GET.get('category', '')
            context['selected_warehouse'] = self.request.GET.get('warehouse', '')
            context['selected_status'] = self.request.GET.get('stock_status', '')
            context['search'] = self.request.GET.get('search', '')
            
            # إجماليات المخزون
            products = self.get_queryset()
            total_quantity = Decimal('0.00')
            total_value = Decimal('0.00')
            for product in products:
                total_quantity += Decimal(str(product.current_quantity))
                total_value += Decimal(str(product.current_quantity)) * Decimal(str(product.purchase_price))
            
            context['total_quantity'] = total_quantity
            context['total_value'] = total_value
        except Exception:
            context['categories'] = []
            context['warehouses'] = []
            context['total_quantity'] = Decimal('0.00')
            context['total_value'] = Decimal('0.00')
        return context


class PurchasesReportView(LoginRequiredMixin, ListView):
    """تقرير المشتريات - عرض فواتير الشراء مع فلترة"""
    model = PurchaseInvoice
    template_name = 'reports/purchases_report.html'
    context_object_name = 'invoices'
    paginate_by = 20
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            
            # فلترة حسب التاريخ
            start_date = self.request.GET.get('start_date', '').strip()
            end_date = self.request.GET.get('end_date', '').strip()
            
            if start_date:
                queryset = queryset.filter(invoice_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(invoice_date__lte=end_date)
            
            # فلترة حسب المورد
            supplier_id = self.request.GET.get('supplier', '').strip()
            if supplier_id:
                queryset = queryset.filter(supplier_id=supplier_id)
            
            return queryset.order_by('-invoice_date')
        except Exception as e:
            messages.error(self.request, "حدث خطأ أثناء جلب تقرير المشتريات.")
            return PurchaseInvoice.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # بيانات الفلترة
            context['suppliers'] = Supplier.objects.filter(is_active=True)
            context['start_date'] = self.request.GET.get('start_date', '')
            context['end_date'] = self.request.GET.get('end_date', '')
            context['selected_supplier'] = self.request.GET.get('supplier', '')
            
            # إجمالي المشتريات
            invoices = self.get_queryset()
            total_amount = Decimal('0.00')
            for invoice in invoices:
                if hasattr(invoice, 'get_total'):
                    total_amount += Decimal(str(invoice.get_total()))
            
            context['total_amount'] = total_amount
            context['invoice_count'] = invoices.count()
        except Exception:
            context['suppliers'] = []
            context['total_amount'] = Decimal('0.00')
            context['invoice_count'] = 0
        return context


class SalesReportView(LoginRequiredMixin, ListView):
    """تقرير المبيعات - عرض فواتير البيع مع فلترة"""
    model = SaleInvoice
    template_name = 'reports/sales_report.html'
    context_object_name = 'invoices'
    paginate_by = 20
    
    def get_queryset(self):
        try:
            queryset = SaleInvoice.objects.filter(status='completed')
            
            # فلترة حسب التاريخ
            start_date = self.request.GET.get('start_date', '').strip()
            end_date = self.request.GET.get('end_date', '').strip()
            
            if start_date:
                queryset = queryset.filter(invoice_date__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(invoice_date__date__lte=end_date)
            
            # فلترة حسب طريقة الدفع
            payment_method = self.request.GET.get('payment_method', '').strip()
            if payment_method:
                queryset = queryset.filter(payment_method=payment_method)
            
            # بحث
            search = self.request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(
                    Q(invoice_number__icontains=search) |
                    Q(customer__name__icontains=search) |
                    Q(customer__phone__icontains=search)
                )
            
            return queryset.order_by('-invoice_date')
        except Exception as e:
            messages.error(self.request, "حدث خطأ أثناء جلب تقرير المبيعات.")
            return SaleInvoice.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # بيانات الفلترة
            context['start_date'] = self.request.GET.get('start_date', '')
            context['end_date'] = self.request.GET.get('end_date', '')
            context['selected_payment'] = self.request.GET.get('payment_method', '')
            context['search'] = self.request.GET.get('search', '')
            
            # إجماليات المبيعات
            invoices = self.get_queryset()
            total_amount = sum((Decimal(str(inv.total)) for inv in invoices), Decimal('0.00'))
            total_paid = sum((Decimal(str(inv.paid_amount)) for inv in invoices), Decimal('0.00'))
            
            context['total_amount'] = total_amount
            context['total_paid'] = total_paid
            context['invoice_count'] = invoices.count()
            
            # إحصائيات طرق الدفع
            context['cash_count'] = invoices.filter(payment_method='cash').count()
            context['card_count'] = invoices.filter(payment_method='card').count()
            context['credit_count'] = invoices.filter(payment_method='credit').count()
        except Exception:
            context['total_amount'] = Decimal('0.00')
            context['total_paid'] = Decimal('0.00')
            context['invoice_count'] = 0
            context['cash_count'] = 0
            context['card_count'] = 0
            context['credit_count'] = 0
        return context


class ProfitsReportView(LoginRequiredMixin, TemplateView):
    """تقرير الأرباح - عرض إجمالي المشتريات والمبيعات والأرباح"""
    template_name = 'reports/profits_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # فلترة حسب التاريخ
            start_date = self.request.GET.get('start_date', '').strip()
            end_date = self.request.GET.get('end_date', '').strip()
            
            # إجمالي المشتريات
            purchases_query = PurchaseDetail.objects.all()
            if start_date:
                purchases_query = purchases_query.filter(invoice__invoice_date__gte=start_date)
            if end_date:
                purchases_query = purchases_query.filter(invoice__invoice_date__lte=end_date)
            
            total_purchases = purchases_query.aggregate(
                total=Sum(F('quantity') * F('purchase_price'))
            )['total'] or Decimal('0.00')
            
            # إجمالي المبيعات
            sales_query = SaleInvoice.objects.filter(status='completed')
            if start_date:
                sales_query = sales_query.filter(invoice_date__date__gte=start_date)
            if end_date:
                sales_query = sales_query.filter(invoice_date__date__lte=end_date)
            
            total_sales = sales_query.aggregate(
                total=Sum('total')
            )['total'] or Decimal('0.00')
            
            # حساب الأرباح
            total_profit = total_sales - total_purchases
            profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else Decimal('0.00')
            
            context['start_date'] = start_date
            context['end_date'] = end_date
            context['total_purchases'] = total_purchases
            context['total_sales'] = total_sales
            context['total_profit'] = total_profit
            context['profit_margin'] = profit_margin
            
            # إحصائيات إضافية
            context['purchase_invoices_count'] = purchases_query.values('invoice').distinct().count()
            context['sale_invoices_count'] = sales_query.count()
            
        except Exception as e:
            messages.error(self.request, f"حدث خطأ أثناء حساب تقرير الأرباح: {str(e)}")
            context.update({
                'start_date': '', 'end_date': '',
                'total_purchases': Decimal('0.00'), 'total_sales': Decimal('0.00'),
                'total_profit': Decimal('0.00'), 'profit_margin': Decimal('0.00'),
                'purchase_invoices_count': 0, 'sale_invoices_count': 0
            })
        return context