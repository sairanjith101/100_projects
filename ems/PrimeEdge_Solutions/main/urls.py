from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_info, name='profile_info'),
    path('employees/', views.employees_page, name='employees'),
    path('company/', views.company_page, name='company'),
    path('help/', views.help_page, name='help'),
    path('leave/', views.leave_apply_page, name='leave_apply'),
    path('head_officers/', views.head_officers_page, name='head_officers'),
    path('attendance/', views.attendance_page, name='attendance'),
    path('logout/', views.logout_view, name='logout'),
]