from django.conf.locale import fa
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Comment, Brand, Category
from django.db.models import Q, Case, When, Value, IntegerField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def product_detail(request, external_id, slug):
    product = get_object_or_404(Product, external_id=external_id)
    comments = product.comments.filter(is_visible=True).order_by('-date_added')
    return render(request, 'product/product_detail.html', {'product': product, 'comments': comments})


def product_list(request, template='product/products_list.html', contexts=None, products=None):
    if products is None:
        products = Product.objects.all()

    paginator = Paginator(products, 1)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    if contexts is None:
        contexts = {'url': ''}
    if 'query' not in contexts:
        contexts['query'] = ""
    contexts.update({'products': page_obj})
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
    products = Product.objects.filter(category=category)
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
        'categories': [{'title': category.name, 'url': category.get_absolute_url()} for category in categories],
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
