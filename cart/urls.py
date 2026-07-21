from django.urls import path
from . import views


app_name = 'cart'
urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/<uuid:external_id>', views.cart_add_view, name='cart_add'),
    path('remove', views.cart_remove_view, name='cart_remove'),
    path('is-in', views.check_cart, name='check_cart'),
    path('checkout', views.checkout_view, name='checkout'),
    path('pay/request', views.send_pay_request_view, name='pay_request'),
    path('pay/verify', views.pay_verify, name='pay_verify'),
    path('discount_code', views.discount_code_view, name='discount_code'),
    path('total_price', views.cart_total_price, name='total_price'),
    path('item_quantity_change', views.cart_item_quantity_change_view, name='item_quantity_change'),
]
