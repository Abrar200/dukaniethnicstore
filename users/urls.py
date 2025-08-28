from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.user_register_view, name='register'),
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('reset_password/', views.password_reset_request_view, name='reset_password'),
    path('reset_password_done/', views.password_reset_done_view, name='password_reset_done'),
    path('reset_password_confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('reset_password_complete/', views.password_reset_complete_view, name='password_reset_complete'),
    path('verify-email/<uidb64>/<token>/', views.EmailVerificationView.as_view(), name='email_verification'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
]