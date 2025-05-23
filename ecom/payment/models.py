from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country  =models.CharField(max_length=255)

    # No pluralizar direcciones
    class Meta:
        verbose_name_plural = "Shipping Address"
    
    def __str__(self):
        return f'Shipping Address - {str(self.id)}'


# Creación de domicilio de envío automático cuando el usuario de logea
def create_shipping(sender,instance,created,**kwargs):
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()

# Automatizar domicilio
post_save.connect(create_shipping,sender=User)


# Order Model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(max_length=150000)
    amount_paid = models.DecimalField(max_digits=7,decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f'Order - {str(self.id)}'
    


# Esta función se ejecuta justo antes de guardar una instancia del modelo Order
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    # Verificamos que la instancia ya existe en la base de datos (o sea, no es una creación nueva)
    if instance.pk:
        # Guardamos la fecha y hora actuales
        now = datetime.datetime.now()

        # Obtenemos la versión actual del objeto desde la base de datos
        # Esto nos permite comparar el valor viejo con el nuevo
        obj = sender._default_manager.get(pk=instance.pk)

        # Comprobamos si el estado de 'shipped' cambió de False a True
        if instance.shipped and not obj.shipped:
            # Si es así, asignamos la fecha actual al campo date_shipped
            instance.date_shipped = now


# Order Items Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7,decimal_places=2)

    def __str__(self):
        return f'Order Item - {str(self.id)}'
