from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from product.models import Product
from .models import Favorite, UserViewHistory


@receiver(user_logged_in)
def sync_session_data_on_login(sender, request, user, **kwargs):
    # sync resent products category viewed
    session_cats = request.session.pop('recent_cats', [])
    for cat_id in session_cats:
        UserViewHistory.objects.update_or_create(user=user, category_id=cat_id)

    # sync favorites list
    fav_ids = request.session.pop('favorites', [])
    if fav_ids:
        valid_products = Product.objects.filter(id__in=fav_ids)
        existing_pids = set(Favorite.objects.filter(user=user, product__in=valid_products)
                            .values_list('product_id', flat=True))
        new_favorites = [Favorite(user=user, product=p) for p in valid_products if p.id not in existing_pids]
        if new_favorites:
            Favorite.objects.bulk_create(new_favorites, ignore_conflicts=True)

    request.session.modified = True