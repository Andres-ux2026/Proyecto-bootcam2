from django import forms


class CheckoutForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        error_messages={'required': 'Debes confirmar la compra para continuar.'},
    )
