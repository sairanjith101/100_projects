from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, 'onlineshop/index.html')

def register(request):
    return render(request, 'onlineshop/register.html')

def collections(request):
    categories = Catagory.objects.filter(status=0)
    return render(request, 'onlineshop/collections.html', {"categories":categories})

def collectionsview(request,name):
    if(Catagory.objects.filter(name=name, status=0)):
        products = Product.objects.filter(catagory__name = name)
        return render(request, 'onlineshop/product.html', {"products":products, "category_name":name})
    else:
        messages.warning(request, "No such Catagory Found")
        return redirect('collections')