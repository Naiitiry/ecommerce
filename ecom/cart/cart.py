from store.models import Product, Profile

class Cart():
    def __init__(self,request):
        self.session = request.session
        # Obtener la request
        self.request = request
        
        # Iniciar la session key si existiera
        cart = self.session.get('session_key')

        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        self.cart = cart

    # Agrega lo de old_cart (en el perfil) y lo convierte para verlo en el carrito
    # cuando se vuelve a logear, ya que al deslogear se borra el mismo del front.
    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)

        if product_id in self.cart:
            pass
        else:
            #self.cart[product_id] = {'price':str(product.price)}
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

        # Lidiar con usuario logeado
        if self.request.user.is_authenticated:
            # Obtener el perfil del actual usuario
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convertir lo guardado en old_cart de dic a json
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            # Guardar carty a el modelo del perfil
            current_user.update(old_cart=str(carty))


    def add(self,product,quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        if product_id in self.cart:
            pass
        else:
            #self.cart[product_id] = {'price':str(product.price)}
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

        # Lidiar con usuario logeado
        if self.request.user.is_authenticated:
            # Obtener el perfil del actual usuario
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convertir lo guardado en old_cart de dic a json
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            # Guardar carty a el modelo del perfil
            current_user.update(old_cart=str(carty))

    def cart_total(self):
        # Get product ID
        product_ids = self.cart.keys()
        # Lookup those keys in our products DB model
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        # Starts counting at 0
        total = 0
        for key, value in quantities.items():
            # Convert key string into, so we can do math
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total = total + (product.sale_price * value)
                    else:
                        total = total + (product.price * value)


        return total


    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        # Tomar las ids del carrito
        product_ids = self.cart.keys()

        # Usar las ids de los productos en la db model
        products = Product.objects.filter(id__in = product_ids)
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)

        # Nuestro carrito
        ourcart = self.cart
        # Actualizar diccionario/carrito
        ourcart[product_id] = product_qty

        self.session.modified = True

        # Lidiar con usuario logeado
        if self.request.user.is_authenticated:
            # Obtener el perfil del actual usuario
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convertir lo guardado en old_cart de dic a json
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            # Guardar carty a el modelo del perfil
            current_user.update(old_cart=str(carty))

        thing = self.cart

        return thing
    
    def delete(self, product):
        product_id = str(product)
        # Delete from dict/cart
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        # Lidiar con usuario logeado
        if self.request.user.is_authenticated:
            # Obtener el perfil del actual usuario
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convertir lo guardado en old_cart de dic a json
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            # Guardar carty a el modelo del perfil
            current_user.update(old_cart=str(carty))
