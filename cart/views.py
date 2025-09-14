from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from cart.cart_module import Cart
from .forms import SelectAddressForm, DiscountCodeForm
from .models import Order, OrderItem, DiscountCode
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import decorators


def cart_detail_view(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


def cart_add_view(request, pk):
    size, color, quantity = request.POST.get('size'), request.POST.get('color'), request.POST.get('quantity')
    cart = Cart(request)
    cart.add(pk, color, size, int(quantity))
    cart_quantity = len(request.session.get('cart', {}))
    return JsonResponse({'cart_quantity': cart_quantity})
    # return redirect('cart:cart_detail')


def cart_remove_view(request):
    uid = request.POST.get('product_id')
    cart = Cart(request)
    cart.remove(uid)
    cart_quantity = len(request.session.get('cart', {}))
    return JsonResponse({'cart_quantity': cart_quantity, 'total_price': cart.total_price()})
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


@require_GET
def checkout_view(request):
    address_form = SelectAddressForm(request.user)
    discount_form = DiscountCodeForm(request.user)
    cart = Cart(request)

    # delete discount_code from session
    session = request.session
    session.pop('discount_code', None)
    session.modified = True

    return render(request, 'cart/checkout.html',
                  {'address_form': address_form, 'discount_form': discount_form, 'cart': cart})


@decorators.login_required(login_url='/account/login')
@require_POST
def order_creation_view(request):
    form = SelectAddressForm(request.user, request.POST)
    if form.is_valid():
        user = request.user
        cart = Cart(request)
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                address=form.cleaned_data.get('address_choice'),
                total_price=cart.total_price(),
            )
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    size=item['size'],
                    color=item['color'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )
            cart.clean_all()

@decorators.login_required(login_url='/account/login')
@require_POST
def discount_code_view(request):
    form = DiscountCodeForm(request.user, request.POST, )
    if form.is_valid():
        discount = form.cleaned_data.get('discount_code')
        cart_total_price = Cart(request).total_price()
        request.session['discount_code'] = discount.percentage
        return JsonResponse({'new_price': f"{cart_total_price - (cart_total_price * discount.percentage / 100):.2f}"})
    return JsonResponse({'error': form.errors}, status=400)


@require_POST
def cart_item_quantity_change_view(request):
    uid, quantity = request.POST.get('uid'), request.POST.get('quantity')
    cart = Cart(request)
    cart.change_quantity(uid, int(quantity))
    return JsonResponse({
        'is_in': True,
        'item_total_price': cart.item_total_price(uid),
        'total_price': cart.total_price()
    })
