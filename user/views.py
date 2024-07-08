from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from django.http import JsonResponse
from datetime import date, datetime, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.models import User
from carinsurance import models as INS_MODAL
from carinsurance import forms as INS_FORM
# Create your views here.
def user_signup_view(request):
    userForm = forms.UserForm()
    customerForm = forms.CustomerForm()
    message = {'status':'SUCCESS', 'data':'Registration is mandatory.'}
    data = {'userForm':userForm, 'customerForm': customerForm, 'message':message}
    if request.method == 'POST':
        userForm = forms.UserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)
        # print('userForm: ',userForm, 'customerForm: ', customerForm)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            print('saved user: ', user)
            # user.set_password(user.password)
            customer =  customerForm.save(commit=False)
            customer.user = user
            customer.save()
            print('saved customer: ', customer)
            customer_group = Group.objects.get_or_create(name='CUSTOMER')
            customer_group[0].user_set.add(user)
        else:
            print('userformerrors: ', userForm.errors, 'customerformerrors: ',customerForm.errors)
        return HttpResponseRedirect('login')
    return render(request, 'user/signup.html', context= data)

@login_required(login_url='login')
def user_dashboard_view(request):
    total_policies = INS_MODAL.Policy.objects.all().count()
    user_cars = INS_MODAL.Car.objects.all().filter(owner=request.user)
    print('usercars: ', user_cars)
    user_policies = INS_MODAL.CarPolicy.objects.filter(car__in=user_cars).count()
    user_claims = INS_MODAL.Claim.objects.filter(policy__car__owner=request.user)
    total_claimed_amount = user_claims.aggregate(Sum('amount'))['amount__sum'] or 0
    print('userclaims: ', user_claims)
    print('total_amt_claimed: ', total_claimed_amount)
    # Count of active claims by the user
    total_active_claims = user_claims.filter(status='Pending').count()
    print('totalpol: ',total_policies, 'user_poli: ', user_policies) #'total_claim: ',total_claimed_amount)
    print('user: ', request.user)
    customer = models.Customer.objects.get(user=request.user)
    print('customer: ', customer)
    data= {
        'user' : customer,
        'total_policies': total_policies,
        'user_policies': user_policies,
        'total_claim': total_claimed_amount,
        'total_active_claims':total_active_claims
    }
    return render(request, 'user/user-dashboard.html',data)

@login_required(login_url='login')
def user_policies_view(request):
    user_cars = INS_MODAL.Car.objects.all().filter(owner=request.user)
    user_policies = INS_MODAL.CarPolicy.objects.filter(car__in=user_cars)
    data ={'user_policies': user_policies, 'user':get_customer_details(request.user)}
    return render(request, 'user/user_policies.html', data)


def get_customer_details(user):
    return models.Customer.objects.get(user=user)

def renew_policy_view(request, pk):
    print('renew policy key: ', pk)
    car_policy = INS_MODAL.CarPolicy.objects.get(id=pk)
    print('car_policy: ', car_policy)
    sum_assurance = car_policy.policy.min_assurance
    data ={'car_policy': car_policy, 'user':get_customer_details(request.user), 'sum_assurance': sum_assurance}
    if request.method == 'POST':
        car_policy.sum_assurance = sum_assurance
        policy = car_policy.policy
        if policy:
            tenure_years = policy.tenure
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=tenure_years*365)
            car_policy.start_date = start_date
            car_policy.end_date = end_date 
            car_policy.is_active=True
            car_policy.save()
            # return HttpResponseRedirect('/user/user_policies')
            return user_policies_view(request)
    return render(request, 'user/renew_policy.html', data)

def user_claims_view(request):
    user_claims = INS_MODAL.Claim.objects.filter(policy__car__owner=request.user)
    data = {'user_claims':user_claims, 'user':get_customer_details(request.user)}
    return render(request, 'user/user_claims.html', data)

def user_cars(request):
    user_cars = INS_MODAL.Car.objects.all().filter(owner=request.user)
    for car in user_cars:
        car_policy = INS_MODAL.CarPolicy.objects.filter(car=car)
        print('car: ', car, 'policy: ', car_policy)
        car.car_policy = car_policy
    data = {'user_cars': user_cars, 'user':get_customer_details(request.user)}
    return render(request, 'user/user_cars.html', data)

def apply_policy_view(request, pk):
    car_policy_form = INS_FORM.CarPolicyForm()
    car = INS_MODAL.Car.objects.get(id=pk)
    if(request.method=='POST'):
         car_policy_form = INS_FORM.CarPolicyForm(request.POST)
        #  print('car_policy_form', car_policy_form)
         if car_policy_form.is_valid:
            car_policy = car_policy_form.save(commit =False)
            car_policy.car = car
            policy = car_policy.policy
            if policy:
                tenure_years = policy.tenure
                start_date = datetime.now().date()
                end_date = start_date + timedelta(days=tenure_years*365)
                car_policy.start_date = start_date
                car_policy.end_date = end_date 
                car_policy.amount_claimed = 0
                car_policy.save()
                print('car_policy: ', car_policy)
            return HttpResponseRedirect('user_policies')
    data = {'form': car_policy_form, 'user':get_customer_details(request.user), 'selected_car':car}
    return render(request, 'user/add_policy.html', data)

def calculate_car_assurance(request, pk):
    print('policy: ', pk, 'car: ', request.GET.get('car'))
    policy = INS_MODAL.Policy.objects.get(policy_id=pk)
    data = {
        'sum_assurance':policy.base_assurance,
        'policy_name':policy.policy_name,
        'premium':policy.premium,
        'tenure':policy.tenure,
        'details':policy.details
    }
    print('data: ', data)
    return JsonResponse(data)
    
def add_car_view(request):
    car_form = INS_FORM.CarForm()
    data = {'user':get_customer_details(request.user),'form':car_form}
    if request.method == 'POST':
        car_form = INS_FORM.CarForm(request.POST)
        if car_form.is_valid:
            car = car_form.save(commit=False)
            car.owner = request.user
            car.save()
            print('new car: ', car)
            return HttpResponseRedirect('user_cars')
    return render(request, 'user/add_car.html', data)

def claim_assurance_view(request, pk):
    car_policy = INS_MODAL.CarPolicy.objects.get(id=pk)
    car_policy.balance = car_policy.sum_assurance - car_policy.amount_claimed
    prev_claims = INS_MODAL.Claim.objects.filter(policy=car_policy)
    form = INS_FORM.ClaimForm()
    data = {'user':get_customer_details(request.user),'previous_claims':prev_claims, 'form':form, 'car_policy':car_policy}
    if request.method == 'POST':
        claim_form = INS_FORM.ClaimForm(request.POST)
        if claim_form.is_valid:
            print('claim_form: :: ', claim_form)
            claim = claim_form.save(commit=False)
            claim.policy = car_policy
            claim.claim_date = datetime.now().date()
            claim.status = "Pending"
            print('claimss: ', claim.description)
            claim.save()
            car_policy.amount_claimed+=claim.amount
            car_policy.save()
            return HttpResponseRedirect('user_claims')
    print('data for claimassurance: ', data)
    return render(request, 'user/claim_assurance.html', data)