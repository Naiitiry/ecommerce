from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile
from django.contrib.auth.models import User
from django import forms

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


# Carga de imagen a Product
class ProductAdminForm(forms.ModelForm):
    image_upload = forms.ImageField(required=False)

    class Meta:
        model = Product
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('image_upload'):
            instance._image_file = self.cleaned_data['image_upload']
        if commit:
            instance.save()
        return instance

class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    readonly_fields = ['image']


# Retirar registro antiguo
admin.site.unregister(User)
admin.site.unregister(Product)

# Poner registro nuevo, permite visualizar/registrar los usuarios a mi conveniencia
admin.site.register(User, UserAmin)

admin.site.register(Product, ProductAdmin)