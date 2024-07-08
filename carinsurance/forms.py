from django import forms
from .models import Category, Policy, Car, CarPolicy, PremiumPolicy, Claim

# Form for the Category model
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

# Form for the Policy model
class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = ['category', 'policy_name', 'base_assurance', 'min_assurance', 'max_assurance', 'premium', 'tenure', 'details']

# Form for the Car model
class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['car_make', 'car_model', 'car_year', 'car_number', 'vin']

# Form for the CarPolicy model
class CarPolicyForm(forms.ModelForm):
    class Meta:
        model = CarPolicy
        fields = ['policy']
       
    def is_valid(self):
        valid = super(CarPolicyForm, self).is_valid()
        for field in self.errors:
            if field != 'policy':
                self.errors.pop(field)
        if 'policy' in self.cleaned_data and not self.cleaned_data['policy']:
            self.add_error('policy', "This field is required.")
        if not self.errors:
            return True
        return False
    def clean(self):
        return super().clean()
        

# Form for the Claim model
class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['amount', 'description', 'damage']

# Form for the PremiumPolicy model
class PremiumPolicyForm(forms.ModelForm):
    class Meta:
        model = PremiumPolicy
        fields = ['policy', 'new_premium', 'effective_date']