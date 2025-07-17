from django import forms
from account.models import Address


class SelectAddressForm(forms.Form):
    address_choice = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        empty_label=None,
        widget=forms.RadioSelect(attrs={'class': 'mr-3 mt-1'}),
        )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        addresses = Address.objects.filter(user=user)
        self.fields['address_choice'].queryset = addresses
        if addresses.exists():
            self.initial['address_choice'] = addresses.first()
