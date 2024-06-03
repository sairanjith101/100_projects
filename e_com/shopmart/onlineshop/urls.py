from django.contrib import admin
from django.urls import path
from onlineshop import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('collections/', views.collections, name='collections')
]
