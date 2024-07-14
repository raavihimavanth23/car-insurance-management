from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Policy(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    policy_id = models.AutoField(primary_key=True)
    policy_name = models.CharField(max_length=200, unique=True)
    base_assurance = models.PositiveIntegerField()
    min_assurance = models.PositiveIntegerField()
    max_assurance = models.PositiveIntegerField()
    premium = models.PositiveIntegerField()
    tenure = models.PositiveIntegerField()
    creation_date = models.DateField(auto_now=True)
    details = models.TextField()

    def __str__(self):
        return self.policy_name

class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    car_make = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    car_year = models.PositiveIntegerField()
    car_number = models.CharField(max_length=20, unique=True)
    vin = models.CharField(max_length=17, unique=True)
    policies = models.ManyToManyField(Policy, through='CarPolicy')
    def __str__(self):
        return f'{self.car_number} - {self.car_make}'

class CarDefect(models.Model):
    name = models.CharField(max_length=100, unique=True, default='')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='defects')
    description = models.CharField(max_length=255)
    severity = models.CharField(max_length=100, choices=[('Low', 'Low'), ('Moderate', 'Moderate'), ('Severe', 'Severe')])
    is_claimed = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.car.car_number} - {self.name}'
class CarPolicy(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    sum_assurance = models.IntegerField()
    amount_claimed = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.car.car_number} - {self.policy.policy_name}"

class Claim(models.Model):
    policy = models.ForeignKey(CarPolicy, on_delete=models.CASCADE)
    claim_date = models.DateField()
    amount = models.PositiveIntegerField()
    description = models.TextField()
    damage = models.ForeignKey(CarDefect, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])
    def __str__(self):
        return f"{self.policy.policy.policy_name} - {self.claim_date}"

class PremiumPolicy(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    new_premium = models.PositiveIntegerField()
    effective_date = models.DateField()

    def __str__(self):
        return f"{self.policy.policy_name} - {self.new_premium}"
