from django.shortcuts import render,redirect,HttpResponse
from .form import CustomUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import json

# Create your views here.
def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, 'onlineshop/index.html', {"products":products})

def add_to_cart(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            product_qty = data['product_qty']
            product_id = data['pid']
            # print(request.user.id)
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Cart'}, status=200)
                else:
                    if product_status.quantity>=product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Product Stock Not Available'}, status=200)            
        else:
            return JsonResponse({'status': 'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status':'Invalid Access'}, status=200)

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out Successfully")
    return redirect("/")

def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == 'POST':
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully")
                return redirect("/")
            else:
                messages.error(request,"Invalid User Name and Password")
                return redirect("/login")
        return render(request, 'onlineshop/login.html')

def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration Success You can Login Now...!")
            return redirect('/login')
    return render(request, 'onlineshop/register.html', {'form': form})

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
