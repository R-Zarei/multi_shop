from django.shortcuts import render
from product.models import Brand


def home(request):
    brands = Brand.objects.all()[:10]
    return render(request, 'home/index.html', {'brands': brands})
