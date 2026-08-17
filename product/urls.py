from django.urls import path
from . import views


app_name = 'product'
urlpatterns = [
    path('<uuid:external_id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('shop/', views.product_list, name='product_list'),
    path('comment/add/', views.add_comment, name='add_comment'),
    path('comment/delete/', views.delete_comment, name='delete_comment'),
    path('comment/edit/', views.edit_comment, name='edit_comment'),
    path('brand/<str:slug>/', views.brand_product_list, name='brand_product_list'),
]
