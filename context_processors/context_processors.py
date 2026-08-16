from account.models import User


def cart_quantity(request):
    return {'cart_count': len(request.session.get('cart', []))}


def favorites_quantity(request):
    if request.user.is_authenticated:
        return {'favorites_count': request.user.favorites.count()}
    else:
        return {'favorites_count': len(request.session.get('favorites', []))}
