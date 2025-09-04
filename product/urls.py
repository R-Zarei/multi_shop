from django.urls import path
from . import views


app_name = 'product'
urlpatterns = [
    path('<uuid:external_id>/<slug:slug>', views.product_detail, name='product_detail'),
    path('shop', views.product_list, name='product_list'),
]
