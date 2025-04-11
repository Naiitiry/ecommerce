from django.shortcuts import render, redirect
from cart.cart import Cart
# Traemos el FORMS y MODELS del envío
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress
from django.contrib import messages

def payment_success(request):
    return render(request,'payment/payment_success.html',{})

def checkout(request):
    # Obtenemos el carrito
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        # Obtenemos el envío
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        # Checkout como usuario autenticado/logeado
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request,'payment/checkout.html',{'cart_products':cart_products,'quantities':quantities,'totals':totals,'shipping_form':shipping_form})
    else:
        # Checkout como visita
        shipping_form = ShippingForm(request.POST or None)
        return render(request,'payment/checkout.html',{'cart_products':cart_products,'quantities':quantities,'totals':totals,'shipping_form':shipping_form})
    
def billing_info(request):
    if request.POST:
        # Obtenemos el carrito
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Verificar si el usuario está logeado
        if request.user.is_authenticated:
            # Tomar el formulario de pago
            billing_form = PaymentForm()
            return render(request,'payment/billing_info.html',{'cart_products':cart_products,'quantities':quantities,'totals':totals,'shipping_info':request.POST,'billing_form':billing_form})
        else:
        # Y si no está logeado
            pass

        shipping_form = ShippingForm(request.POST or None)
        return render(request,'payment/billing_info.html',{'cart_products':cart_products,'quantities':quantities,'totals':totals,'shipping_form':shipping_form})
    else:
        messages.error(request,'Access Denied!')
        return redirect('home')