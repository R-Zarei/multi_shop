

def cart_quantity(request):
    return {'count': len(request.session.get('cart', []))}
