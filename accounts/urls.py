from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # تسجيل الدخول
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    
    # تسجيل الخروج
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # الملف الشخصي
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # تعديل الملف الشخصي
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # تغيير كلمة السر
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # تسجيل مستخدم جديد
    path('register/', views.RegisterView.as_view(), name='register'),
]