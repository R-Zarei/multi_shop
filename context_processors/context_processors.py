from account.models import User
from product.models import Category


def cart_quantity(request):
    return {'cart_count': len(request.session.get('cart', []))}


def favorites_quantity(request):
    if request.user.is_authenticated:
        return {'favorites_count': request.user.favorites.count()}
    else:
        return {'favorites_count': len(request.session.get('favorites', []))}


def categories(request):
    root_categories = Category.objects.filter(parent=None).prefetch_related('children__children')
    return {'root_categories': root_categories}
