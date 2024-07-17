from django.contrib import admin
from django.urls import path
from onlineshop import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('collections/', views.collections, name='collections'),
    path('collections/<str:name>/', views.collectionsview, name='collections'),
    path('collections/<str:cname>/<str:pname>/', views.product_details, name='product_details'),
]
