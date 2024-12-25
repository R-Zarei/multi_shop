from django.shortcuts import render
from .models import Product


def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'product/product_detail.html', {'product': product})
