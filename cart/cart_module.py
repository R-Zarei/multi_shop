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
        cart_items = self.cart.copy()
        products_ids = [item['product_id'] for item in cart_items.values()]
        products = {p.id: p for p in Product.objects.filter(id__in=products_ids)}

        for item in cart_items.values():
            product = products.get(item['product_id'])
            yield {
                **item, # add all key value in item dict.
                'product': product,
                'total': int(product.price) * int(item.get('quantity', 0)),
                'unique_id': f"{item['product_id']}-{item['color']}-{item['size']}"
            }

    def add(self, pk: int, color: str, size: str, quantity: int) -> None:
        if quantity <= 0:
            return
        unique_id = f'{pk}-{color}-{size}'
        if unique_id in self.cart:
            self.cart[unique_id]['quantity'] += int(quantity)
        else:
            self.cart[unique_id] = {
                'product_id': pk,
                'color': color,
                'size': size,
                'quantity': int(quantity)
            }
        self.save()

    def clean_all(self) -> None:
        del self.session[cart_session_id]
        self.save()

    def remove(self, uid: str):
        if uid in self.cart:
            del self.cart[uid]
            self.save()

    def change_quantity(self, uid: str, quantity: int = 0) -> None:
        if uid in self.cart and quantity > 0:
            self.cart[uid]['quantity'] = quantity
            self.save()

    def item_total_price(self, uid: str) -> int:
        item = self.cart.get(uid)
        if item is None:
            return 0
        product = Product.objects.get(id=item['product_id'])
        return product.price * item.get('quantity', 0)

    # @property
    def total_price(self):
        product_ids = [item['product_id'] for item in self.cart.values()]
        product_prices = {p.id: p.price for p in Product.objects.filter(id__in=product_ids)}
        total = 0
        for item in self.cart.values():
            product_price = product_prices.get(item['product_id'])
            if product_price:
                total += product_price * item.get('quantity', 0)
        return total

    def save(self):
        self.session.modified = True
