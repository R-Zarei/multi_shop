from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import (UserLoginForm, UserRegistrationForm, OtpForm, LoginWithOtpForm, UserProfileForm, ChangePasswordForm,
                    AddressForm)
from django.contrib.auth import login, logout, decorators
from .models import User, City, Address
from kavenegar import KavenegarAPI
from random import randint
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from django.utils.html import escape

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


def user_login_with_opt(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = LoginWithOtpForm(request.POST)
        if form.is_valid():
            rand_code = randint(1000, 9999)
            print(rand_code)
            '''response = SMS.sms_send(
                {'receptor': str(cd.get('phone')), 'message': f'Multi Shop\nVerification code: {rand_code}'})'''
            request.session.set_expiry(120)
            request.session['opt'] = {'phone': form.cleaned_data['phone'],
                                      'code': rand_code,
                                      'full_name': None,
                                      'password': None}
            return redirect(reverse('account:check_otp'))
    else:
        form = LoginWithOtpForm()

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
            user, created = User.objects.get_or_create(phone=user_info['phone'],
                                                       defaults=({'full_name': user_info['full_name']}))
            # get_or_create() doesn't hash password to create user that's why we use set_password for the user.
            if created:
                user.set_password(user_info['password'])
                user.save()
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


@decorators.login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'account/user_profile.html', {'form': form})


@decorators.login_required
def change_password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been updated.')
            return redirect('account:profile')
    else:
        form = ChangePasswordForm()
    return render(request, 'account/change_password.html', {'form': form})


@decorators.login_required
def user_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return JsonResponse({
                "error": False,
                "id": address.id,
                "province": str(address.province),
                "city":  str(address.city),
                "addr": escape(address.address),
                "zipcode": address.zipcode,
            })
        else:
            return JsonResponse({
                "error": True,
                "error_s": form.errors,
                "non_find_error": 2
            })
    else:
        form = AddressForm()
        addresses = Address.objects.filter(user=request.user)
        return render(request, 'account/user_address.html', {"form": form, "addresses": addresses})


@decorators.login_required
@require_GET
def lode_city(request):
    province_id = request.GET.get("province_id")
    if province_id:
        cities = City.objects.filter(province_id=province_id).order_by('name')
        return JsonResponse(list(cities.values("id", "name")), safe=False)
    return JsonResponse([], safe=False)


# @decorators.login_required
@require_POST
def remove_address(request):
    try:
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        address.delete()
        return JsonResponse({"success": True})
    except ModuleNotFoundError:
        return JsonResponse({"success": False})


@decorators.login_required
@require_POST
def edit_address(request):
    try:
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "error": False,
                "address_id": address.id,
                "province": str(address.province),
                "city": str(address.city),
                "addr": escape(address.address),
                "zipcode": address.zipcode,
            })
        else:
            return JsonResponse({
                'error': True,
                'error_s': form.errors,
            })

    except ModuleNotFoundError:
        return JsonResponse({"success": False})
