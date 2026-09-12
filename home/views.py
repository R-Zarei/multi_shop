from django.shortcuts import render
from product.models import Brand, Category, Product
from account.models import UserViewHistory
from django.db.models import Q


def suggestion_products(request, limit=10):
    if request.user.is_authenticated:
        recent_cat_ids = list(
            UserViewHistory.objects.filter(user=request.user).values_list('category_id', flat=True)[:5])
    else:
        recent_cat_ids = request.session.get('recent_cats', [])

    if recent_cat_ids:
        categories = Category.objects.filter(id__in=recent_cat_ids)
        parent_ids = [c.parent_id for c in categories if c.parent_id]

        suggested_products = Product.objects.prefetch_related('images').filter(
            Q(category_id__in=recent_cat_ids) | Q(category__parent_id__in=parent_ids)).distinct().order_by('?')[:limit]
    else:
        suggested_products = Product.objects.prefetch_related('images').all().order_by('?')[:limit]

    return suggested_products


def home(request):
    context = {
        'brands': Brand.objects.all().order_by('?')[:15],
        'categories': Category.objects.filter(children__isnull=True).order_by('?')[:16],
        'suggested_products': suggestion_products(request, 16)
    }
    return render(request, 'home/index.html', context)
