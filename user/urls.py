from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from carinsurance import views
from . import views as user_views
urlpatterns = [

    # path('customerclick', views.afterlogin_view,name='customerclick'),
    path('signup', user_views.user_signup_view,name='user_signup'),
    # path('customer-dashboard', views.customer_dashboard_view,name='customer-dashboard'),
    path('login', LoginView.as_view(template_name='user/login.html'),name='user_login'),
    path('user-dashboard', user_views.user_dashboard_view,name='user_dashboard'),
    path('user-policies', view= user_views.user_policies_view, name='user_policies'),
    path('renew-policy/<int:pk>',user_views.renew_policy_view, name='renew_policy'),
    path('add-policy/<int:pk>',user_views.apply_policy_view, name='add_policy'),
    path('user-claims',user_views.user_claims_view, name='user_claims'),
    path('user-cars', user_views.user_cars, name = 'user_cars'),
    path('calculate-assurance-covered/<int:pk>', user_views.calculate_car_assurance, name='calculate_assurance_covered'),
    path('add-car', user_views.add_car_view,name='add_car'),
    path('claim-assurance/<int:pk>', user_views.claim_assurance_view, name='claim_assurance'),
    # path('apply/<int:pk>', views.apply_view,name='apply'),
    # path('history', views.history_view,name='history'),

    # path('ask-question', views.ask_question_view,name='ask-question'),
    # path('question-history', views.question_history_view,name='question-history'),
]