from typing import Any, Dict
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . import models

class UserForm(UserCreationForm):
    class Meta:
        model=User
        fields=['first_name', 'last_name','username','email']
    def clean_first_name(self):
        fname = self.cleaned_data['first_name']
        if not fname:
            raise forms.ValidationError('First name is required')
        return fname
    def clean_last_name(self):
        lname = self.cleaned_data['last_name']
        if not lname:
            raise forms.ValidationError('Last name is required')
        return lname
    def clean_password2(self) -> str:
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if not password2 or password1!=password2:
            raise forms.ValidationError("password and confirm password does not match.")
        return password2
    def clean_password1(self) -> str:
        password1 = self.cleaned_data['password1']
        if not password1:
            raise forms.ValidationError('Password is Invalid')
        return password1
class CustomerForm(forms.ModelForm):
    class Meta:
        model=models.Customer
        fields=['address','phone','profile_photo']
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone or not phone.isdigit() or len(phone)!=10:
            raise forms.ValidationError("Phone should be 10 digits numbers")
        return phone
    def clean_profile_photo(self):
        profile_photo = self.cleaned_data['profile_photo']
        if profile_photo:
            if profile_photo.content_type not in ['image/jpeg', 'image/png']:
                raise forms.ValidationError("Profile photo should be in JPEG or PNG format.")
            if profile_photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Profile picture should not exceed 2MB.")
        return profile_photo
    def clean_address(self):
        address = self.cleaned_data['address']
        if not address:
            raise forms.ValidationError("address should be not be empty.")
        return address