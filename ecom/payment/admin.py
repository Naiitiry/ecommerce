from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User


# registrar modelo en el Admin
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)


# Crear un OrderItem en linea
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

# Extender nuestro modelo de Order
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user","full_name","email","shipping_address","amount_paid","date_ordered","shipped","date_shipped"]
    inlines = [OrderItemInline]

# Sacar del registro al modelo Order (que está arroba: admin.site.register(Order))
admin.site.unregister(Order)

# Re-registrar modelo Order y OrderAdmin
admin.site.register(Order,OrderAdmin)