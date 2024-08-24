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

def favviewpage(request):
    if request.user.is_authenticated:
        fav=Favourite.objects.filter(user=request.user)
        return render(request, 'onlineshop/fav.html', {"fav":fav})
    else:
        return redirect("/")
    
def remove_fav(request,fid):
    item = Favourite.objects.get(id=fid)
    item.delete()
    return redirect("/favviewpage")

def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request, 'onlineshop/cart.html', {"cart":cart})
    else:
        return redirect("/")
    
def remove_cart(request,cid):
    cartitem = Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart")

def fav_page(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)            
        else:
            return JsonResponse({'status': 'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status':'Invalid Access'}, status=200)

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

def purchase_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            product_id = request.POST.get('product_id')
            print(f"Product ID received: {product_id}")  # Debug

            if product_id:
                try:
                    # Fetch the specific product and its cart item
                    product = Product.objects.get(id=product_id)
                    print(f"Product found: {product.name}")  # Debug

                    cart_item = Cart.objects.get(user=request.user, product=product)
                    print(f"Cart item found for user: {request.user.username}")  # Debug

                    # Delete the specific cart item
                    cart_item.delete()

                    messages.success(request, f'Product "{product.name}": Thank you! Your purchase has been completed.')
                except Product.DoesNotExist:
                    messages.error(request, 'Product not found.')
                except Cart.DoesNotExist:
                    messages.error(request, 'Item not found in your cart.')

            else:
                messages.error(request, 'No product specified.')

            return redirect('cart') 
        else:
            return redirect('/login')
    else:
        return redirect('cart')