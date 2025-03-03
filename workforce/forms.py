
from django import forms
from .models import OptimizationParameters

class OptimizationForm(forms.ModelForm):
    class Meta:
        model = OptimizationParameters
        fields = [
            'skilled_cost', 
            'semi_skilled_cost', 
            'skilled_production', 
            'semi_skilled_production',
            'budget', 
            'min_production', 
            'max_skilled_workers', 
            'max_semi_skilled_workers'
        ]
        widgets = {
            'skilled_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'semi_skilled_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'skilled_production': forms.NumberInput(attrs={'class': 'form-control'}),
            'semi_skilled_production': forms.NumberInput(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_production': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_skilled_workers': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_semi_skilled_workers': forms.NumberInput(attrs={'class': 'form-control'}),
        }
