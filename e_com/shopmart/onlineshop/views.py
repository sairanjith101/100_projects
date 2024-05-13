from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'onlineshop/index.html')

def register(request):
    return render(request, 'onlineshop/register.html')