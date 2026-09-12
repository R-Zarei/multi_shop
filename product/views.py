# from django.conf.locale import fa
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from jedi.plugins import django

from .models import Product, Comment, Brand, Category, Discount, Color, Size
from django.db.models import Q, Value, IntegerField
from django.core.paginator import Paginator
from django.db.models import Case, When
from decimal import Decimal
from account.models import UserViewHistory
from django.template.loader import render_to_string


def get_similar_products(product, limit=5):
    final_price = product.final_price
    min_price = final_price * Decimal(0.7)
    max_price = final_price * Decimal(1.3)

    similar = Product.objects.filter(category=product.category).exclude(id=product.id)

    return similar.order_by(Case(
        When(brand=product.brand, price__range=(min_price, max_price), then=0),
        When(price__range=(min_price, max_price), then=1),
        When(brand=product.brand, then=1),
        default=2),'?')[:limit]


def record_category_view(request, category):
    if not category:
        return

    if request.user.is_authenticated:
        UserViewHistory.objects.update_or_create(user=request.user, category=category)
    else:
        recent_cats = request.session.get('recent_cats', [])
        if category.id in recent_cats:
            recent_cats.remove(category.id)
        recent_cats.insert(0, category.id)
        request.session['recent_cats'] = recent_cats[:5]
        request.session.modified = True


def product_detail(request, external_id, slug):
    product = get_object_or_404(Product, external_id=external_id)
    comments = product.comments.filter(is_visible=True).order_by('-date_added')
    record_category_view(request, product.category)  # save resent activity
    return render(request, 'product/product_detail.html', {
        'product': product,
        'comments': comments,
        'suggestions': get_similar_products(product),
    })


def product_list(request, template='product/products_list.html', contexts=None, products=None):
    if products is None:
        products = Product.objects.all().order_by('?')

    # give filter values from GET
    price_val = request.GET.get('price')
    colors = request.GET.getlist('color')
    sizes = request.GET.getlist('size')

    # price filter
    if price_val and price_val != 'all':
        try:
            min_p, max_p = price_val.split('-')
            products = products.filter(price__gte=min_p, price__lte=max_p)
        except ValueError:
            pass

    # color filter
    if colors:
        products = products.filter(color__name__in=colors)

    # size filter
    if sizes:
        products = products.filter(size__title__in=sizes)

    products = products.distinct()

    paginator = Paginator(products, 12)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    if contexts is None:
        contexts = {}

    contexts.setdefault('url', '')
    contexts.setdefault('query', '') # use for search products view
    contexts['colors'] = Color.objects.all()
    contexts['sizes'] =  Size.objects.all()
    contexts['products'] = page_obj

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        html = render_to_string('product/includes/products_partial.html', contexts, request=request)
        return JsonResponse({'html': html})

    return render(request, template_name=template, context=contexts)


@login_required()
@require_POST
def add_comment(request):
    external_id = request.POST.get('external_id')
    if not external_id:
        return JsonResponse({'success': False, 'error': 'Product ID is required!'}, status=400)

    product = Product.objects.filter(external_id=external_id).first()
    if not product:
        return JsonResponse({'success': False, 'error': 'Product not found!'}, status=404)

    text = request.POST.get('text')
    if not text:
        return JsonResponse({'success': False, 'error': 'Comment text is required!'}, status=400)

    comment = Comment.objects.create(product=product, user=request.user, text=text)

    return JsonResponse({
        'success': True,
        'id': comment.id,
        'text': comment.text,
        'date': comment.last_modified.strftime('%d %b %Y'),
        'comment_count': comment.product.comments.filter(is_visible=True).count(),
    })


@login_required()
@require_POST
def delete_comment(request):
    comment_id = request.POST.get('comment_id')
    if not comment_id:
        return JsonResponse({'success': False, 'error': 'Comment ID is required!'}, status=400)

    comment = Comment.objects.filter(id=comment_id).first()
    if not comment:
        return JsonResponse({'success': False, 'error': 'Comment not found!'}, status=404)

    if request.user != comment.user:
        return JsonResponse({'success': False, 'error': 'You are not allowed to delete comment!'}, status=403)

    comment.is_visible = False
    comment.save()

    return JsonResponse({
        'success': True,
        'id': comment.id,
        'comment_count': comment.product.comments.filter(is_visible=True).count(),
    })


@require_POST
@login_required()
def edit_comment(request):
    comment_id = request.POST.get('comment_id')
    if not comment_id:
        return JsonResponse({'success': False, 'error': 'Comment ID is required!'}, status=400)

    comment_text = request.POST.get('text')
    if not comment_text:
        return JsonResponse({'success': False, 'error': 'Comment text is required!'}, status=400)

    comment = Comment.objects.filter(id=comment_id).first()
    if not comment:
        return JsonResponse({'success': False, 'error': 'Comment not found!'}, status=404)

    if request.user != comment.user:
        return JsonResponse({'success': False, 'error': 'You are not allowed to edit comment!'}, status=403)

    comment.text = comment_text
    comment.save()

    return JsonResponse({
        'success': True,
        'id': comment.id,
        'last_modified': comment.last_modified.strftime('%d %b %Y'),
        'text': comment.text,
    })


def brand_product_list(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = Product.objects.filter(brand=brand)
    context = {'brand': brand, 'url': brand.get_absolute_url()}
    return product_list(request, template='product/brand_products_list.html', contexts=context, products=products)
    # return render(request, 'product/brand_products_list.html', {'brand': brand, 'products': products})


def category_product_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    category_children = category.children.all()
    childes = [category]
    if category_children:
        childes.extend(category_children)
        for child in category_children:
            childes.extend(child.children.all())

    products = Product.objects.filter(category__in=childes).order_by('-id')
    context = {'category': category, 'url': category.get_absolute_url()}
    return product_list(request, template='product/category_products_list.html', contexts=context, products=products)
    # return render(request, 'product/category_products_list.html', {'category': category, 'products': products})


@require_POST
def search_suggestions(request):
    query = request.POST.get('query', '').strip()

    products = Product.objects.filter(title__icontains=query).annotate(
        priority=Case(
            When(title__iexact=query, then=Value(1)),
            When(title__istartswith=query, then=Value(2)),
            When(title__icontains=query, then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('priority')[:5]

    # products = Product.objects.filter(title__icontains=query)[:5]
    brands = Brand.objects.filter(name__icontains=query)[:5]
    categories = Category.objects.filter(name__icontains=query)[:5]

    return JsonResponse({
        'products': [{'title': product.title, 'url': product.get_absolute_url()} for product in products],
        'brands': [{'title': brand.name.upper(), 'url': brand.get_absolute_url()} for brand in brands],
        'categories': [{'title': category.get_full_path(), 'url': category.get_absolute_url()} for category in categories],
    })


@require_GET
def search_product(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(brand__name__icontains=query) |
        Q(category__name__icontains=query)
    )
    context = {'url': request.path, 'query': query}
    return product_list(request, contexts=context, products=products)

@require_GET
def offer_product(request, percent):
    discounts = Discount.objects.filter(percentage=percent)
    if not discounts.exists():
        raise Http404("No discount with this percentage was found.")

    all_products = Product.objects.filter(discount__in=discounts)
    return product_list(request, contexts={'url': request.path}, products=all_products)

