from django import forms
from .models import Investment


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        # adjust the fields to match your model
        fields = ["coin", "quantity"]
        widgets = {
            "coin": forms.TextInput(attrs={"placeholder": "BTC"}),
            "quantity": forms.NumberInput(attrs={"step": "any"}),
        }
