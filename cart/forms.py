from django.utils import timezone
from django import forms
from django.core.exceptions import ValidationError
from account.models import Address
from .models import DiscountCode, DiscountCodeUsage


class SelectAddressForm(forms.Form):
    address_choice = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        empty_label=None,
        widget=forms.RadioSelect(attrs={'class': 'mr-3 mt-1'}),
        )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        addresses = Address.objects.filter(user=user)
        self.fields['address_choice'].queryset = addresses
        if addresses.exists():
            self.initial['address_choice'] = addresses.first()

    def clean_address_choice(self):
        address = self.cleaned_data['address_choice']
        if address.user == self.user:
            return address
        raise ValidationError('This address does not belong to you.')


class DiscountCodeForm(forms.Form):
    discount_code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control border-0 p-4',
            'placeholder': 'Discount code',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_discount_code(self):
        discount_code = self.cleaned_data['discount_code']
        try:
            discount = DiscountCode.objects.get(code=discount_code)
        except DiscountCode.DoesNotExist:
            raise ValidationError("This discount code is invalid!")

        if discount.quantity <= 0:
            raise ValidationError("This discount code is no longer valid.")

        if discount.valid_until < timezone.now():
            raise ValidationError("This discount code has expired.")

        if DiscountCodeUsage.objects.filter(user=self.user, discount=discount).exists():
            raise ValidationError("This discount code has already been used.")

        return discount

