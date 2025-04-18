from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django import forms
from django.db.models import Q
import json
from cart.cart import Cart


def search(request):
    # Determinar si llenaron el formulario
    if request.method == 'POST':
        searched = request.POST['searched']
        # Buscar, por querys, los productos
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        # Test for null
        if not searched:
            messages.error(request,'Ese producto no existe!')
            return render(request,'search.html',{})
        else:
            return render(request,'search.html',{'searched':searched})
    else:
        return render(request,'search.html',{})


def update_info(request):
    if request.user.is_authenticated:
        # Obtener el usuario actual
        current_user = Profile.objects.get(user__id=request.user.id)
        # Obtener el envío del usuario actual
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        # Obtener formulario original del usuario
        form = UserInfoForm(request.POST or None, instance=current_user)
        # Obtener formulario de envío del usuario
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            # Guardar formulario de usuario
            form.save()
            # Guardar formulario de envío
            shipping_form.save()

            messages.success(request,'Tu información ha sido actualizada.')
            return redirect('home')
        return render(request,'update_info.html',{'form':form,'shipping_form':shipping_form})
    else:
        messages.error(request,'Tienes que estar logeado!')
        return redirect('home')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user,request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,'Tu contraseña fue actualizada correctamente, relogea!')
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request,error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request,'update_password.html',{'form':form})
    else:
        return redirect('home')


def update_user(request,):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request,current_user)
            messages.success(request,'Usuario actualizado!.')
            return redirect('home')
        return render(request,'update_user.html',{'user_form':user_form})
    else:
        messages.error(request,'Tienes que estar logeado.')
        return redirect('home')


def category_summary(request):
    categories = Category.objects.all()
    return render(request,'category_summary.html',{'categories':categories})


def category(request,foo):
    foo = foo.replace('-',' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request,'category.html',{'products':products,'category':category})
    except:
        messages.error(request,"Esa categoría no existe.")
        return redirect('home')

def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request,'product.html',{'product':product})

def home(request):
    products = Product.objects.all()
    return render(request,'home.html',{'products':products})

def about(request):
    return render(request,'about.html',{})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)

            # Que hacer con las cosas del carrito
            current_user = Profile.objects.get(user__id=request.user.id)
            # Traer lo guardado del carrito en la BD
            saved_cart = current_user.old_cart
            # Convertir DB string a dic
            if saved_cart:
                # convertir a dic con JSON (una función de este último)
                converted_cart = json.loads(saved_cart)
                # Agregarlo diccionario a la sesión
                # Traer el carrito (traer el cart.py de la app cart)
                cart = Cart(request)
                # Hacer un loop del carrito y de los items en el
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request,"Tienes que estar logeado.")
            return redirect('home')
        else:
            messages.error(request,"Hubo un error, intenta logearte nuevamente.")
            return redirect('login')
    else:
        return render(request,'login.html',{})

def logout_user(request):
    logout(request)
    messages.success(request,("Te deslogeaste!."))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # login user
            user = authenticate(username=username,password=password)
            login(request,user)
            messages.success(request,"Te registraste correctamente - Por favor, completá la información de usuario abajo.")
            return redirect('update_info')
        else:
            messages.error(request,"UPS! hubo un problema en el registro!.")
            return redirect('register')
    else:
        return render(request,'register.html',{'form':form})