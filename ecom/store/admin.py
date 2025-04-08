from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile
from django.contrib.auth.models import User

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)


# Mezclar información del perfíl e información del usuario
class ProfileInLine(admin.StackedInline):
    model = Profile

# Extender el Modelo de Usuario
class UserAmin(admin.ModelAdmin):
    model = User
    field = ['username','first_name','last_name','email']
    inlines = [ProfileInLine]


# Retirar registro antiguo
admin.site.unregister(User)

# Poner registro nuevo, permite visualizar/registrar los usuarios a mi conveniencia
admin.site.register(User, UserAmin)