from django.shortcuts import render, redirect
from .forms import UserLoginForm
from django.contrib.auth import login, decorators
from .models import User


def user_login(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = User.objects.get(phone=form.cleaned_data['phone'])
            login(request, user)
            return redirect('/')
    else:
        form = UserLoginForm()
    return render(request, 'account/login.html', {'form': form})