from .carinsurance_exception import CarInsuranceException
from .exception.user_exception import UserException
from datetime import datetime
from  . import date_util as du
def is_empty(value):
    return value is None or len(value)<=0

def is_not_empty(value):
    return value is not None and len(value) >0
def is_greater(value1, value2):
    return value1 > value2
def is_between(min, between, max):
    return min <= between and between <=max

def validate_year(year):
    return  year < datetime.now().year and (year+20 > datetime.now().year)
        
def is_policy_valid(policy):
    if is_empty(policy):
        return False
    if not policy.policy_name:
        return False
    if not policy.base_assurance:
        return False
    if not policy.min_assurance:
        return False
    if not policy.max_assurance:
        return False
    pass

def is_car_valid(car):
    if not car:
        raise CarInsuranceException("Please enter car details.")
    if is_empty(car.car_make):
        raise CarInsuranceException("Car Brand is required")
    if is_empty(car.car_model):
        raise CarInsuranceException("Car Model is required")
    if not validate_year(car.car_year):
        raise CarInsuranceException("Invalid car year")
    if car.car_year > du.datetime.now().year:
        raise CarInsuranceException("Car year is invalid")
    if not car.car_number:
        raise CarInsuranceException("Car number is required")
    if not car.vin or len(car.vin) !=17:
        raise CarInsuranceException("Vehicle Identification Number should be 17 characters")

def is_phone_valid(phone):
    pass 
def is_customer_valid(customer):
    if not customer:
        raise UserException("Invalid Customer Details!")
    if not customer.phone:
        raise UserException("Invalid phone number")
    if not customer.address:
        raise UserException("Invalid address. Should be upto 100 characters")
    if not customer.profile_photo:
        raise UserException("Profile Photo is required")

def validate_user(user):
    if not user:
        raise UserException("Invalid User")
    if not user.username:
        raise UserException("Invalid username")
    if not user.password:
        raise UserException("Invalid password")
    if not user.email:
        raise UserException("Invalid email")

def check_apply_policy(car_policy):
    if not car_policy or not car_policy.car or not car_policy.policy:
        raise CarInsuranceException("Policy and Car both required")
    car = car_policy.car
    policy = car_policy.policy
    if not validate_year(car.car_year):
        raise CarInsuranceException("car is too old for policy.")
    if not is_between(policy.min_assurance, car_policy.sum_assurance, policy.max_assurance):
        raise CarInsuranceException("sum assurance is not within the policy assurance range")
    if du.is_after(car_policy.start_date, car_policy.end_date):
        raise CarInsuranceException("start date should be less than end date")
    if du.date_plus(car_policy.start_date, policy.tenure) < car_policy.end_date:
        raise CarInsuranceException("End Date is greater policy tenure")
    

def check_claim(claim):
    if claim.damage.is_claimed:
        raise CarInsuranceException(f"{claim.damage} is already claimed")
    if claim.amount <=0:
        raise CarInsuranceException('claim amount should be greater than 0')
    car_policy = claim.policy
    if not car_policy:
        raise CarInsuranceException("CarPolicy is not defined")
    if not car_policy.is_active or car_policy.end_date < du.date.today() :
        raise CarInsuranceException("This CarPolicy is  inactive/expired")
    bal_amt = car_policy.sum_assurance - car_policy.amount_claimed
    if bal_amt < claim.amount:
        raise CarInsuranceException(f"Claim amount {claim.amount} is greater than balance amount: {bal_amt}")