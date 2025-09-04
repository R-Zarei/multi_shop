from django.shortcuts import render, get_object_or_404
from .models import Product


def product_detail(request, external_id, slug):
    product = get_object_or_404(Product, external_id=external_id)
    return render(request, 'product/product_detail.html', {'product': product})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product/shop.html', {'products': products})