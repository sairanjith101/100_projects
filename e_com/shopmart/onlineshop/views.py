from django.shortcuts import render,redirect,HttpResponse
from .models import *
from django.contrib import messages

# Create your views here.
def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, 'onlineshop/index.html', {"products":products})

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
    
def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname, status=0)):
        if(Product.objects.filter(name=pname, status=0)):
            products = Product.objects.filter(name=pname,status=0).first()
            return render(request, 'onlineshop/product_details.html', {"products":products})
        else:
            messages.error(request, "No such Product Found")
            return redirect('collections')
    else:
        messages.error(request, "No such Category Found")
        return redirect('collections')
