from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.core import validators
from django.contrib.auth import authenticate
from account.models import User
from django.contrib.auth.hashers import make_password


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['phone', "email", "full_name"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['phone', "email", "password", "full_name", "is_active", "is_admin"]


def start_with_zero(value):  # custom validator.
    if value[0] != '0':
        raise ValidationError('Please enter a valid phone number', code='invalid_phone', )


class UserLoginForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Phone Number'}),
                            validators=[start_with_zero])
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'Password'}))

    def clean(self):
        phone = self.cleaned_data.get('phone')
        password = self.cleaned_data.get('password')
        if not authenticate(username=phone, password=password):
            raise ValidationError("Incorrect phone or password!")

    # can use "validators = [validators.MaxLengthValidator(11)])" in "phone" fild.
    def clean_phone(self):
        phone_number = self.cleaned_data.get('phone')
        if len(phone_number) != 11:
            raise ValidationError("Phone number must be 11 digits", code='invalid_phone',
                                  params={'value': f'{phone_number}'})
        return phone_number


class UserRegistrationForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Phone Number'}),
                            validators=[start_with_zero])
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Full name'}), )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'Password'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'Password confirmation'}))

    def clean(self):  # check phone number already taken.
        if User.objects.filter(phone=self.cleaned_data.get('phone')).exists():
            raise ValidationError('This phone number is already taken', code='phone_taken')

        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            raise ValidationError("Passwords don't match", code='password_mismatch')

    def clean_phone(self):
        phone_number = self.cleaned_data.get('phone')
        if len(phone_number) != 11:
            raise ValidationError("Phone number must be 11 digits", code='invalid_phone')
        return phone_number


class OtpForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Enter Verification Code'}))


class LoginWithOtpForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Phone Number'}),
                            validators=[start_with_zero])

    def clean_phone(self):
        phone_number = self.cleaned_data.get('phone')
        if len(phone_number) != 11:
            raise ValidationError("Phone number must be 11 digits", code='invalid_phone')

        if not User.objects.filter(phone=phone_number).exists():
            raise ValidationError('This phone number not found', code='invalid_phone')

        return phone_number


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email']
        widgets = {
            # 'phone': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Phone Number'}),
            'full_name': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'class': "form-control", 'placeholder': 'Email'}),
            # 'password': forms.PasswordInput(
            #    attrs={'class': "form-control", 'placeholder': 'Password', 'required': False}),
        }


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'Old Password'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'Password confirmation'}))

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("Old password incorrect", code='password_incorrect')
        return old_password

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError("Passwords don't match", code='password_mismatch')

    def save(self, commit=True):
        password = self.cleaned_data.get('password')
        self.user.set_password(password)
        if commit:
            self.user.save()
