from django.contrib import admin

# Register your models here.
from .models import  Car,CarPolicy, Claim, PremiumPolicy, Policy, Category

admin.site.register(Car)
admin.site.register(CarPolicy)
admin.site.register(Claim)
admin.site.register(Policy)
admin.site.register(PremiumPolicy)
admin.site.register(Category)