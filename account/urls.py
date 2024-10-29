from django.urls import path
from . import views


app_name = 'account'
urlpatterns = [
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('register', views.user_register, name='register'),
    path('checkotp', views.check_opt, name='check_otp'),
    path('login/opt', views.user_login_with_opt, name='login_with_opt'),
]