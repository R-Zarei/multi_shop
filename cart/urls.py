from django.urls import path
from . import views


app_name = 'cart'
urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/<int:pk>', views.cart_add_view, name='cart_add'),
    path('remove', views.cart_remove_view, name='cart_remove'),
    path('is-in', views.check_cart, name='check_cart'),
]
