from django.contrib import admin
from django.urls import path
from shop import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
]
