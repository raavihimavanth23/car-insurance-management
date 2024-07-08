from django.shortcuts import render,redirect,reverse
from . import models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.models import User
from carinsurance import models
from user.models import Customer
# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('post_login')  
    return render(request,'common/index.html')

def postlogin_view(request):
    if is_user_customer(request.user):
        return redirect('user/user-dashboard')
    return redirect('/admin/')

def is_user_customer(user):
    print('checking user in customer group', user)
    return user.groups.filter(name='CUSTOMER').exists()
@login_required
def all_policies_view(request):
    policies = models.Policy.objects.all()
    print('all-policies: ', policies)
    customer = Customer.objects.get(user=request.user)
    return render(request, 'user/all_policies.html',{'policies':policies, 'user': customer})