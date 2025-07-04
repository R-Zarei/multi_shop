from django.urls import path
from . import views


app_name = 'account'
urlpatterns = [
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('register', views.user_register, name='register'),
    path('checkotp', views.check_opt, name='check_otp'),
    path('login/otp', views.user_login_with_opt, name='login_with_opt'),
    path('profile', views.edit_profile, name='profile'),
    path('change_password', views.change_password, name='change_password'),
    path('address', views.user_address, name='user_address'),
    path('address/load_city', views.lode_city, name="lode_city"),
    path('remove_address', views.remove_address, name='remove_address'),
    path('edit_address', views.edit_address, name='edit_address'),
]
