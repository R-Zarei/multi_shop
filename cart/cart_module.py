from product.models import Product

cart_session_id = 'cart'


# product id: "id-color-size"
class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(cart_session_id)
        if not self.cart:
            self.cart = self.session[cart_session_id] = {}

    def __iter__(self):
        cart = self.cart.copy()
        for item in cart.values():
            product = Product.objects.get(id=item['product_id'])
            item['product'] = product
            item['total'] = int(product.price) * int(item.get('quantity', 0))
            item['unique_id'] = f'{item['product_id']}-{item['color']}-{item['size']}'
            yield item

    def add(self, pk: int, color, size, quantity):
        unique_id = f'{pk}-{color}-{size}'
        if unique_id not in self.cart:
            self.cart[unique_id] = {'product_id': pk, 'color': color, 'size': size, 'quantity': int(quantity)}
        else:
            self.cart[unique_id]['quantity'] += int(quantity)

        self.save()

    def remover(self, uid: str):
        if uid in self.cart:
            del self.cart[uid]
            self.save()

    def total_price(self):
        cart = self.cart.values()
        total = 0
        for item in cart:
            product = Product.objects.get(id=item['product_id'])
            total += product.price * item.get('quantity', 0)
        return total

    def save(self):
        self.session.modified = True
