from django import forms
from .models import Order
from .models import Feedback


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'country', 'state', 'city', 'poscode']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['food_item', 'rating', 'comment']
        widgets = {
            'food_item': forms.HiddenInput()
        }

class GuestOrderForm(forms.ModelForm):
    guest_name = forms.CharField(max_length=100, required=True)
    guest_email = forms.EmailField(required=True)
    guest_phone = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = Order
        fields = ['guest_name', 'guest_email', 'guest_phone']