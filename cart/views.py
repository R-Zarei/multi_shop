from django.db import transaction,models
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from cart.cart_module import Cart
from .forms import SelectAddressForm, DiscountCodeForm
from .models import Order, OrderItem, DiscountCode, DiscountCodeUsage
from product.models import Size, Color
from product.models import Product
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import decorators
from .zarinpal import ZarinPal


def cart_detail_view(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def cart_add_view(request, external_id):
    size, color, quantity = request.POST.get('size'), request.POST.get('color'), request.POST.get('quantity')
    cart = Cart(request)
    product = Product.objects.get(external_id=external_id)
    if product:
        cart.add(product.id, color, size, int(quantity))
        cart_quantity = len(request.session.get('cart', {}))
        return JsonResponse({'cart_quantity': cart_quantity})
    return JsonResponse({'error': 'Invalid request'}, status=400)


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
    cart = Cart(request)
    if cart.is_empty():
        return redirect('cart:cart_detail')
    address_form = SelectAddressForm(request.user)
    discount_form = DiscountCodeForm(request.user)

    # delete discount_code from session
    session = request.session
    session.pop('discount_code', None)
    session.modified = True

    return render(request, 'cart/checkout.html',
                  {'address_form': address_form, 'discount_form': discount_form, 'cart': cart})


# creat order and its item.
def order_creation(request):
    try:
        user = request.user
        form = SelectAddressForm(user, request.POST)
        if form.is_valid():
            cart = Cart(request)
            with transaction.atomic():
                order = Order.objects.create(
                    user=user,
                    address=form.cleaned_data.get('address_choice'),
                    total_price=cart.total_price(),
                )
                for item in cart:
                    size = None
                    if item['size']:
                        size = Size.objects.get(title=item['size'])
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        size=size,
                        color=Color.objects.get(name=item['color']),
                        quantity=item['quantity'],
                        price=item['product'].price
                    )
                cart.clean_all()
            return order
        return False
    except Exception as e:
        print(e)
        return False


pay = ZarinPal(merchant='a0640e64-c74f-4c36-a26a-63e291ab8b39', call_back_url='http://127.0.0.1:8000/cart/pay/verify')


@decorators.login_required(login_url='/account/login')
@require_POST
def send_pay_request_view(request):
    order = order_creation(request)
    if order:
        # check and apply discount code.
        amount = order.total_price
        discount_code_id = request.session.get('discount_code')
        if discount_code_id:
            discount = get_object_or_404(DiscountCode, id=discount_code_id)
            amount -= (amount * discount.percentage / 100)

        response = pay.send_request(amount=str(int(amount)), description='Payment for shopping from multi-shop',
                                    mobile=request.user.phone)
        if response.get('error_code') is None:
            request.session['order_id'] = order.id
            # redirect object
            return response
        else:
            return render(request, 'cart/error_page.html',
                          {'error_code': response.get("error_code"), 'error_message': response.get("message")})
    return HttpResponse('order dont carate')


def pay_verify(request):
    order = get_object_or_404(Order, id=request.session.get('order_id'))
    amount = order.total_price
    discount_code = request.session.get('discount_code')
    if discount_code:
        discount_code = get_object_or_404(DiscountCode, id=discount_code)
        amount -= (amount * discount_code.percentage / 100)

    # delete discount_code and order_id from session
    session = request.session
    session.pop('discount_code', None)
    session.pop('order_id', None)
    session.modified = True

    response = pay.verify(request=request, amount=str(int(amount)))

    if response.get("transaction"):
        if response.get("pay"):
            order.is_paid = True
            order.save()
            if discount_code:
                DiscountCodeUsage.objects.create(user=request.user, discount=discount_code, order=order)
                discount_code.quantity = models.F('quantity') - 1
                discount_code.save(update_fields=['quantity'])
            return render(request, 'cart/pay_message_page.html',
                          {'message': f'REF ID: {response.get("RefID")}'})
        else:
            return render(request, 'cart/pay_message_page.html',{'message': response.get("message")})
    else:
        if response.get("status") == "ok":
            return render(request, 'cart/error_page.html',
                          {'error_code': response.get("error_code"), 'error_message': response.get("message")})
        elif response.get("status") == "cancel":
            return render(request, 'cart/error_page.html',
                          {
                              'error_code': 'The transaction failed or was canceled by the user.',
                              'error_message': response.get("message")
                          })
    return redirect('cart:cart_detail')


@decorators.login_required(login_url='/account/login')
@require_POST
def discount_code_view(request):
    form = DiscountCodeForm(request.user, request.POST, )
    if form.is_valid():
        discount = form.cleaned_data.get('discount_code')
        cart_total_price = Cart(request).total_price()
        request.session['discount_code'] = discount.pk
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
