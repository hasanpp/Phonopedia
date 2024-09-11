from django.shortcuts import redirect
from django.urls import path,include
from . import views 

from allauth.account.views import LogoutView
from .views import auto_redirect_to_google
def google_login_redirect(request):
    return redirect('account_social_login', provider='google')

urlpatterns = [
    path('signin', views.signin,name='signin'),
    path('admin_signin', views.admin_signin,name='admin_signin'),
    path('admin_forgot_password', views.admin_forgot_password,name='admin_forgot_password'),
    path('Admin_verify', views.Admin_verify,name='Admin_verify'),
    path('signup', views.signup,name='signup'),
    path('signout', views.signout,name='signout'),
    path('email_varification', views.email_varification,name='email_varification'),
    path('change_password', views.change_password,name='change_password'),
    path('old_password/<int:user_id>', views.old_password,name='old_password'),
    path('admin_change_password', views.admin_change_password,name='admin_change_password'),
    path('forgot_password', views.forgot_password,name='forgot_password'),
    path('otp_chec', views.otp_chec,name='otp_chec'),
    path('account_details', views.account_details,name='account_details'),
    path('accounts/', include('allauth.urls')),
    path('accounts/google/login/', auto_redirect_to_google),
    path('accounts/login/', google_login_redirect, name='account_login'),
    path('accounts/logout/', LogoutView.as_view(), name='account_logout'),
    path('verify-referral-code/', views.verify_referral_code, name='verify_referral_code'),

]

