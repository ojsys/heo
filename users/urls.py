from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/<int:pk>/', views.UserUpdateView.as_view(), name='profile_update'),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_field_name='next'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('verify/', views.verification_view, name='verify'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('password-change/', auth_views.PasswordResetView.as_view(
        template_name='users/password_change.html',
        success_url='/password-change/done/'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),
]