from django.shortcuts import render,redirect
from . import forms,models
from django import forms as DJFORM
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from carinsurance import models as INS_MODAL
from carinsurance import forms as INS_FORM
from library.insurance_calculator import calculate_max_assurance
import library.validate as validate
from library.document_helper import DocumentHelper,DocumentException
from library import date_util as du
from library.carinsurance_exception import CarInsuranceException
import os
import boto3
session = boto3.Session(
    aws_access_key_id= os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.getenv('S3_SECRET_KEY')
)
s3_storage_url = "https://x23101083-carinsurance.s3.eu-west-1.amazonaws.com/"

def login_view(request):
    form = forms.UserForm()
    data = {'form':form}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password1')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/post_login')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'user/login.html', context = data)

# Create your views here.
def user_signup_view(request):
    userForm = forms.UserForm()
    customerForm = forms.CustomerForm()
    # message = {'status':'SUCCESS', 'data':'Registration is mandatory.'}
    data = {'userForm':userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.UserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)
        # print('userForm: ',userForm, 'customerForm: ', customerForm)
        try:
            if userForm.is_valid() and customerForm.is_valid():
                user = userForm.save()
                print('saved user: ', user)
                customer =  customerForm.save(commit=False)
                customer.user = user
                profile_photo  = request.FILES["profile_photo"]
                # print('profile_pic: ', profile_photo)
                # filename = DocumentHelper.upload(profile_photo, user,s3 = boto3.resource('s3'))
                # customer.profile_photo.url = s3_storage_url+filename
                customer.save()
                print('saved customer: ', customer)
                customer_group = Group.objects.get_or_create(name='CUSTOMER')
                customer_group[0].user_set.add(user)
                return HttpResponseRedirect('login')
            else:
                messages.error(request, userForm.errors)
                messages.error(request, customerForm.errors)
        except DJFORM.ValidationError as e:
            print('exception :',str(e))
            messages.error(request, str(e))
        
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

@login_required(login_url='login')
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
            start_date = du.datetime.date
            end_date = du.date_plus(start_date, tenure_years*365)
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
                sum_assurance = calculate_max_assurance(car, policy, [])
                end_date = start_date + timedelta(days=tenure_years*365)
                car_policy.start_date = start_date
                car_policy.end_date = end_date 
                car_policy.amount_claimed = 0
                car_policy.sum_assurance = sum_assurance
                validate.check_apply_policy(car_policy)
                car_policy.save()
                print('car_policy: ', car_policy)
            return HttpResponseRedirect('/user/user-policies')
    data = {'form': car_policy_form, 'user':get_customer_details(request.user), 'selected_car':car}
    return render(request, 'user/add_policy.html', data)

def calculate_car_assurance(request, pk):
    print('policy: ', pk, 'car: ', request.GET.get('car'))
    policy = INS_MODAL.Policy.objects.get(policy_id=pk)
    car = INS_MODAL.Car.objects.get(id= request.GET.get('car'))
    car_policy = INS_MODAL.CarPolicy.objects.filter(car = car)
    print('car details: ', car.car_model, 'car_policy: ', car_policy)
    previous_claims = []
    for cp in car_policy:
        previous_claims.append(INS_MODAL.Claim.objects.filter(policy = cp))
    print('previous claims: ', previous_claims)
    car_assurance = calculate_max_assurance(car, policy, previous_claims)
    data = {
        'sum_assurance':car_assurance,
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
        try:
            if car_form.is_valid:
                car = car_form.save(commit=False)
                car.owner = request.user
                validate.is_car_valid(car)
                car.save()
                print('new car: ', car)
                return HttpResponseRedirect('/user/user-cars')
            else:
                messages.error(request, car_form.errors)
        except CarInsuranceException as e:
            print('Adding car error: ', e)
            messages.error(request, str(e))
    return render(request, 'user/add_car.html', data)

def claim_assurance_view(request, pk):
    car_policy = INS_MODAL.CarPolicy.objects.get(id=pk)
    car_policy.balance = car_policy.sum_assurance - car_policy.amount_claimed
    prev_claims = INS_MODAL.Claim.objects.filter(policy=car_policy)
    form = INS_FORM.ClaimForm()
    data = {'user':get_customer_details(request.user),'previous_claims':prev_claims, 'form':form, 'car_policy':car_policy}
    try:
        if request.method == 'POST':
            claim_form = INS_FORM.ClaimForm(request.POST)
            if claim_form.is_valid :
                print('claim_form: :: ', claim_form)
                claim = claim_form.save(commit=False)
                claim.policy = car_policy
                claim.claim_date = datetime.now().date()
                claim.status = "Pending"
                validate.check_claim(claim)
                print('claim damage: ', claim.damage)
                claim.save()
                car_policy.amount_claimed+=claim.amount
                car_policy.save()
                damage =  claim.damage
                damage.is_claimed=True
                damage.save()
                return HttpResponseRedirect('/user/user-claims')
    except CarInsuranceException as e:
        data['status'] = 'ERROR'
        data['message'] = e.message
    print('data for claimassurance: ', data)
    return render(request, 'user/claim_assurance.html', data)

def car_damages_view(request):
    cars = INS_MODAL.Car.objects.filter(owner = request.user)
    car_damages = []
    for car in cars:
        car_damages.extend(INS_MODAL.CarDefect.objects.filter(car = car ))
    data = {'user': get_customer_details(request.user), 'car_damages': car_damages}
    print('car damages: data: ',data)
    return render(request, 'user/car_damages.html', data)
def get_car(id):
    return INS_MODAL.Car.objects.get(id=id)

def add_damage_view(request):
    damage_form = INS_FORM.CarDefectForm()
    if request.method == 'POST':
        damage_form = INS_FORM.CarDefectForm(request.POST)
        if damage_form.is_valid:
            damage = damage_form.save(commit=False)
            print('damage: ', damage)
            damage.save()
            return HttpResponseRedirect('/user/car-damages')
        else:
            messages.error(request, damage_form.errors)
    data = {'user': get_customer_details(request.user), 'form' : damage_form}
    return render(request, 'user/add_damage.html', data)