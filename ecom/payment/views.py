from django.shortcuts import render, redirect
from cart.cart import Cart
# Traemos el FORMS y MODELS del envío
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages
from django.contrib.auth.models import User
from store.models import Product, Profile
import datetime




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

        # Crear una sesión con Información de Envío
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

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
    
def process_order(request):
    if request.POST:
        # Obtenemos el carrito
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        # tomar los datos de pago de la última página
        payment_form = PaymentForm(request.POST or None)
        # tomar los datos de envío de la sesión
        my_shipping = request.session.get('my_shipping')

        # Reunir información de la orden
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        # Crear domicilio de envío con la info de la sesión
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}\n"
        amount_paid = totals

        # Creamos la orden
        if request.user.is_authenticated:
            # logged in
            user = request.user

            # Creamos la orden, con toda la información actualizada
            create_order = Order(user=user,full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
            create_order.save()

            ### Agregar elementos de la orden - traídos de models.py OrderItem
            # Obtener el ID de la orden
            order_id = create_order.pk

            # Obtener la información del producto
            for product in cart_products():
                # Obetenemos el ID del producto
                product_id = product.id
                # Obtenemos el precio del producto
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                # Obtenemos Cantidad
                for key,value in quantities().items():
                    if int(key) == product.id:
                        # Crear item de la orden
                        create_order_item = OrderItem(order_id=order_id ,product_id=product_id , user=user, quantity=value, price=price)
                        create_order_item.save()
            # Eliminar el carrito una vez pagado
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Eliminar Key
                    del request.session[key]
            
            # Eliminar el carrito de la BD (old_cart)
            currente_user = Profile.objects.filter(user__id=request.user.id)
            # Eliminar carrito de compras
            currente_user.update(old_cart="")

            messages.success(request,'Pago realizado!')
            return redirect('home')
        else:
            # Creamos la orden, con toda la información actualizada
            create_order = Order(full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
            create_order.save()
            ### Agregar elementos de la orden - traídos de models.py OrderItem
            # Obtener el ID de la orden
            order_id = create_order.pk

            # Obtener la información del producto
            for product in cart_products():
                # Obetenemos el ID del producto
                product_id = product.id
                # Obtenemos el precio del producto
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                # Obtenemos Cantidad
                for key,value in quantities().items():
                    if int(key) == product.id:
                        # Crear item de la orden
                        create_order_item = OrderItem(order_id=order_id ,product_id=product_id , quantity=value, price=price)
                        create_order_item.save()
        
            # Eliminar el carrito una vez pagado
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Eliminar Key
                    del request.session[key]


            messages.error(request,'No logeado')
            return redirect('home')
    else:
        messages.error(request,'Acceso denegado!')
        return redirect('home')

# # # # # # # # # # DASHBOARD SHIP # # # # # # # # # # 

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            
            num = request.POST['num']
            # Obtener la orden
            order = Order.objects.filter(id=num)
            # Actualizar el estado
            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=now)
            messages.success(request,'Estado del envío actualizado.')
            return redirect('home')

        return render(request,"payment/not_shipped_dash.html",{"orders":orders})
    else:
        messages.success(request,"Acceso denegado!")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            
            num = request.POST['num']
            # Obtener la orden
            order = Order.objects.filter(id=num)
            # Actualizar el estado
            now = datetime.datetime.now()
            order.update(shipped=False, date_shipped=now)
            messages.success(request,'Estado del envío actualizado.')
            return redirect('home')


        return render(request,"payment/shipped_dash.html",{"orders":orders})
    else:
        messages.success(request,"Acceso denegado!")
        return redirect('home')
    
def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Obtener la orden
        order = Order.objects.get(id=pk)
        # Obtenemos los items de la orden
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipped_status']
            # Verificar si es falso o verdadero
            if status == 'true':
                # Obtener la orden
                order = Order.objects.filter(id=pk)
                # Actualizar el estado
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                # Obtener la orden
                order = Order.objects.filter(id=pk)
                # Actualizar el estado
                order.update(shipped=False)
            messages.success(request,'Estado del envío actualizado.')
            return redirect('home')

        return render(request,'payment/orders.html',{"order":order,"items":items})
    else:
        messages.success(request,"Acceso denegado!")
        return redirect('home')