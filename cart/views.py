from django.http import JsonResponse
from django.shortcuts import render, redirect
from cart.cart_module import Cart
from .forms import SelectAddressForm
from django.views.decorators.http import require_POST, require_GET


def cart_detail_view(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


def cart_add_view(request, pk):
    size, color, quantity = request.POST.get('size'), request.POST.get('color'), request.POST.get('quantity')
    cart = Cart(request)
    cart.add(pk, color, size, quantity)
    cart_quantity = len(request.session.get('cart', {}))
    return JsonResponse({'cart_quantity': cart_quantity})
    # return redirect('cart:cart_detail')


def cart_remove_view(request):
    uid = request.POST.get('product_id')
    cart = Cart(request)
    cart.remover(uid)
    cart_quantity = len(request.session.get('cart', {}))
    return JsonResponse({'cart_quantity': cart_quantity})
    # return redirect('cart:cart_detail')


@require_POST
def check_cart(request):
    cart = Cart(request)
    uid = request.POST.get('product_id')
    for product in cart:
        if uid == product['unique_id']:
            return JsonResponse({'is_in': True})
    return JsonResponse({'is_in': False})


@require_GET
def cart_total_price(request):
    cart = Cart(request)
    return JsonResponse({'total_price': cart.total_price()})


def order_detail_view(request):
    form = SelectAddressForm(request.user)
    return render(request, 'cart/order_detail.html', {'form': form})


