from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem


# registrar modelo en el Admin
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

