from django.shortcuts import render, redirect
from .forms import UserLoginForm, UserRegistrationForm, OtpForm
from django.contrib.auth import login, logout, decorators
from .models import User, Otp
from kavenegar import KavenegarAPI
from random import randint
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone

SMS = KavenegarAPI(apikey='484236523838636B4178655269387331566A7932673638786D6C6155376B7944554137435A3973424335733D')


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


def user_logout(request):
    logout(request)
    return redirect('/')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            rand_code = randint(1000, 9999)
            print(rand_code)
            '''response = SMS.sms_send(
                {'receptor': str(cd.get('phone')), 'message': f'Multi Shop\nVerification code: {rand_code}'})'''
            # otp = Otp.objects.create(phone=cd.get('phone'), rand_code=rand_code, full_name=cd['full_name'], password=cd['password'])
            request.session.set_expiry(120)
            request.session['opt'] = {'phone': cd.get('phone'),
                                      'code': rand_code,
                                      'full_name': cd.get('full_name'),
                                      'password': cd.get('password')}
            return redirect(reverse('account:check_otp'))  # + f'?token={otp.token}')
    else:
        form = UserRegistrationForm()

    return render(request, 'account/register.html', {'form': form})


def check_opt(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = OtpForm(request.POST)
        user_info = request.session.get('opt', {})
        if form.is_valid() and user_info and int(form.cleaned_data.get('code')) == user_info.get('code'):
            user = User.objects.create_user(phone=user_info['phone'], full_name=user_info['full_name'],
                                            password=user_info['password'])
            login(request, user)
            return redirect('/')
        else:
            form.add_error('code', 'Verification code is invalid')
    else:
        form = OtpForm()

    return render(request, 'account/check_otp.html', {'form': form})


'''
if request.method == 'POST':
        form = OtpForm(request.POST)
        token = request.GET.get('token')
        if form.is_valid():
            try:
                user_info = Otp.objects.get(token=token, rand_code=form.cleaned_data['code'])
                if user_info.expiration_date + timedelta(minutes=2) < timezone.now():
                    user_info.delete()
                    del user_info
                user = User.objects.create_user(phone=user_info.phone, full_name=user_info.full_name, password=user_info.password)
                user_info.delete()
                login(request, user)
                return redirect('/')
            except:
                otp = Otp.objects.filter(token=token)
                if otp.exists():
                    otp.delete()
                form.add_error('code', 'Verification code is invalid')
'''
