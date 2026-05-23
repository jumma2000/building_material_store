# accounts/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, UpdateView, FormView, CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User


class ProfileView(LoginRequiredMixin, TemplateView):
    """عرض الملف الشخصي للمستخدم"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """تعديل الملف الشخصي"""
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الملف الشخصي بنجاح')
        return super().form_valid(form)


class ChangePasswordView(LoginRequiredMixin, FormView):
    """تغيير كلمة السر"""
    template_name = 'accounts/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('accounts:profile')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'تم تغيير كلمة السر بنجاح')
        return super().form_valid(form)


class RegisterView(CreateView):
    """تسجيل مستخدم جديد"""
    template_name = 'accounts/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم إنشاء الحساب بنجاح. يمكنك تسجيل الدخول الآن.')
        return response