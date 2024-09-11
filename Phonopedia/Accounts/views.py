from django.shortcuts import render,redirect
from Users.models import Custom_User as User
from django.contrib.auth import login as authlogin,logout,authenticate
from django.contrib.auth.decorators import login_required,user_passes_test
from admin_panel.views import admin_panel
from django.views.decorators.cache import never_cache
from django.contrib import messages
from Home.views import home
from django.core.mail import send_mail
from django.conf import settings
from .forms import varification
from datetime import datetime, timedelta
import pyotp
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import oauth2_login
from Users.models import Address,Profile,Wallet
from django.http import JsonResponse


# Create your views here.
OTP_VALIDITY_PERIOD = 1
secret_key = pyotp.random_base32()
@never_cache
def signin(request):
    if request.user.is_authenticated :
        return redirect(home)
    if request.method == 'POST' :
        username = request.POST['username']
        if not User.objects.filter(username=username):
            messages.error(request,'Ther is no user name like this')
            return redirect(signin)
        account = User.objects.get(username=username)
        if account.is_active :
            pass
        else :
            messages.error(request,'This account is temporary bolcked')
            return redirect(signin)
        password = request.POST['password']
        user=authenticate(username=username ,password=password)
        if user:
            authlogin(request, user)
            return redirect(home)
        else :
            messages.error(request,'Please check the username and password')
            return redirect(signin)
    return render(request,'signin.html')

@never_cache
def admin_signin(request):
    if request.user.is_authenticated:
        user_id = request.session.get("_auth_user_id")
        user = User.objects.get(pk=user_id)
        if user.is_staff:
            return redirect(admin_panel)
        else:
            return redirect(home)
    # User=None
    if request.method == 'POST' :
        username = request.POST['username']
        password = request.POST['password']
        user=authenticate(username=username ,password=password)
        if user and user.is_staff==True:
            authlogin(request, user)
            return redirect(admin_panel)
        else :
            messages.error(request,'Please check the username and password')
            return redirect(admin_signin)
    return render(request,'admin/signin.html')

def forgot_password(request):
    request.session['type'] = 'exist'
    return render(request,'Confirm_email.html')

def admin_forgot_password(request):
    form = varification()
    if request.method == 'POST':
        if not User.objects.filter(email=request.POST['email']).exists():
            messages.error(request, 'This mail id do not have an account in Phonopedia')
            return redirect(admin_forgot_password)
        user = User.objects.get(email=request.POST['email'])
        if user.is_staff:
            form = varification(request.POST)
            if form.is_valid():
                print('hi')
                request.session['email'] = request.POST['email']
                subject = 'Email varification PhonoPedia'
                totp = pyotp.TOTP(secret_key)
                otp = totp.now()
                request.session['otp'] = otp
                message = f'Your otp is ({otp}).Use this otp to verify your email id to change your passsword for admin account in phonopedia'
                recipient = form.cleaned_data.get('email')
                send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=False)
                return redirect(Admin_verify)
        else :
            messages.error(request,'This mail id do not the admin')
            return redirect(admin_forgot_password)
    return render(request,'admin/forgetpassword.html')

def change_password(request):
    if request.method == 'POST' :
        email = request.session['email']
        print(email)
        user = User.objects.get(email=email)
        user.set_password(request.POST['password']) 
        user.save()
        return redirect(signin)
    return render(request,'change_password.html')

def old_password(request, user_id):
    if request.method == 'POST' :
        password = request.POST['password']
        username = User.objects.get(pk=user_id).username
        user_P=authenticate(username=username ,password=password)
        
        if user_P:
            request.session['email'] = user_P.email
            return redirect(change_password)
        else :
            messages.error(request,'The old password was wrong')
            return redirect(old_password,user_id)
        
    return render(request,'old_password.html') 

def admin_change_password(request):
    if request.method == 'POST' :
        email = request.session['email']
        user = User.objects.get(email=email)
        user.set_password(request.POST['password']) 
        user.save()
        request.session.flush()
        messages.success(request,'Password was changed sussesfuly')
        return redirect(admin_signin)
    return render(request,'admin/change_password.html')
def signout(request):
    if request.session.session_key:
        user_id = request.session.get("_auth_user_id")
        user = User.objects.get(pk=user_id)
        if user.is_staff:
            logout(request)
            return redirect(admin_signin)
        else:
            logout(request)
            return redirect(home)
    # logout(request)
    # return redirect(home)

@never_cache
def signup(request):
    if request.user.is_authenticated :
        return redirect(home)
    user=None
    error_message=None
    if request.method == 'POST' :
        try :
            email = request.POST.get('email')
            request.session['username'] = request.POST['username']
            request.session['password'] = request.POST['password']
            request.session['email'] = request.POST['email']
            request.session['f_name'] = request.POST['f_name']
            request.session['l_name'] = request.POST['l_name']
            request.session['phone'] = request.POST['phone']
            request.session['type'] = 'notexisting'
            return render(request,'Confirm_email.html',{'email':email})
        except Exception as e:
             messages.error = "This username or email address is already taken. Please choose another one."
             return redirect(signup)
    return render(request, 'signup.html', {'user': user, 'error_message': error_message})
@never_cache
def email_varification(request):
    form = varification()
    if request.method == 'POST':
        form = varification(request.POST)
        if form.is_valid():
            request.session['email'] = request.POST['email']
            subject = 'Email varification PhonoPedia'
            totp = pyotp.TOTP(secret_key)
            otp = totp.now()
            request.session['otp'] = otp
            message = f'Your otp is ({otp}).Use this otp to verify your email id to signup on PhonoPedia. Please do not share this otp with any one'
            recipient = form.cleaned_data.get('email')
            send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=False)
            if request.session['type'] == 'exist':
                if not User.objects.filter(email=request.POST['email']).exists():
                    messages.error(request, 'This mail id do not have an account in Phonopedia')
                    return redirect(email_varification)
            return redirect(otp_chec) 
    return render(request, 'Confirm_email.html', {'form': form})
@never_cache
def otp_chec(request):
    if request.method == 'POST':
        if 'resend_otp' in request.POST:
            # Resend OTP logic
            totp = pyotp.TOTP(secret_key)
            otp = totp.now()
            request.session['otp'] = otp
            request.session['otp_created_at'] = datetime.now().timestamp()

            # Resend the email
            subject = 'Resend OTP - PhonoPedia'
            message = f'Your new OTP is ({otp}). Use this to verify your email. Please do not share this OTP with anyone.'
            recipient = request.session['email']
            send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=False)

            messages.success(request, 'A new OTP has been sent to your email.')
            return redirect(otp_chec)

        otp_c = request.POST['otp']
        otp = request.session.get('otp')
        otp_created_at = datetime.fromtimestamp(request.session.get('otp_created_at', datetime.now().timestamp()))
        
        # Check if OTP is still valid
        if datetime.now() > otp_created_at + timedelta(minutes=OTP_VALIDITY_PERIOD):
            messages.error(request, 'The OTP has expired. Please request a new one.')
            return redirect(otp_chec)
        
        if int(otp) == int(otp_c):
            email = request.session['email']
            if request.session['type'] == 'exist':
                request.session['email'] = email
                return redirect(change_password)
            username = request.session['username']
            password = request.session['password']
            phone = request.session['phone']
            f_name = request.session['f_name']
            l_name = request.session['l_name']
            referral_code = request.session.get('valid_referral_code', None)
            user = User.objects.create_user(username=username, password=password, email=email, first_name=f_name, last_name=l_name, phone=phone)
            if referral_code:
                referrer_profile = Profile.objects.get(referral_code=referral_code)
                referrer = referrer_profile.user

                # Add balance to referrer wallet
                referrer_wallet = Wallet.objects.get_or_create(user=referrer)
                referrer_wallet = Wallet.objects.get(user=referrer)
                referrer_wallet.balence += 550 
                referrer_wallet.save()
                print("re : ",referrer_wallet.user.username)
                # Add balance to new user wallet
                user_wallet  = Wallet.objects.get_or_create(user=user,balence=0)
                user_wallet  = Wallet.objects.get(user=user)
                user_wallet.balence += 1000
                user_wallet.save()
                # Clear the referral code from session
                del request.session['valid_referral_code']
                
            request.session.flush()
            return redirect(signin)
        else:
            messages.error(request, 'The OTPs do not match.')
            return redirect(otp_chec)
    otp_created_at = datetime.fromtimestamp(request.session.get('otp_created_at', datetime.now().timestamp()))
    time_left = max(0, (otp_created_at + timedelta(minutes=OTP_VALIDITY_PERIOD) - datetime.now()).seconds)
    return render(request, 'verifyemail.html', {'time_left': time_left}) 
@never_cache
def Admin_verify(request):
    if request.method == 'POST':
        if 'resend_otp' in request.POST:
            # Resend OTP logic
            totp = pyotp.TOTP(secret_key)
            otp = totp.now()
            request.session['otp'] = otp
            request.session['otp_created_at'] = datetime.now().timestamp()

            # Resend the email
            subject = 'Resend OTP - PhonoPedia'
            message = f'Your new OTP is ({otp}). Use this to verify your email. Please do not share this OTP with anyone.'
            recipient = request.session['email']
            send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=False)

            messages.success(request, 'A new OTP has been sent to your email.')
            return redirect(Admin_verify)

        otp_c = request.POST['otp']
        otp = request.session.get('otp')
        otp_created_at = datetime.fromtimestamp(request.session.get('otp_created_at', datetime.now().timestamp()))
        
        # Check if OTP is still valid
        if datetime.now() > otp_created_at + timedelta(minutes=OTP_VALIDITY_PERIOD):
            messages.error(request, 'The OTP has expired. Please request a new one.')
            return redirect(Admin_verify)
        
        if int(otp) == int(otp_c):
            email = request.session['email']
            return redirect(admin_change_password)
            
        else:
            messages.error(request, 'The OTPs do not match.')
            return redirect(Admin_verify)
    otp_created_at = datetime.fromtimestamp(request.session.get('otp_created_at', datetime.now().timestamp()))
    time_left = max(0, (otp_created_at + timedelta(minutes=OTP_VALIDITY_PERIOD) - datetime.now()).seconds)
    return render(request, 'admin/verify_otp.html', {'time_left': time_left}) 
@never_cache
def account_details(request):
    if request.user.is_authenticated :
        user = User.objects.get(username = request.user)
        addresses = Address.objects.filter(user = user)
        if request.method == 'POST' :
            username = request.POST['username']
            # email = request.POST['email']
            f_name = request.POST['f_name']
            l_name = request.POST['l_name']
            phone = request.POST['phone']
            # old_email = user.email
            
            if user.username != username:
                user_check = User.objects.filter(username=username)
                if user_check:
                    messages.error(request,'this username is already taken')
                else:
                    user.username = username 
            
            user.first_name = f_name
            user.last_name = l_name
            user.phone = phone
            user.save()
        profile = Profile.objects.get_or_create(user=user)
        profile = Profile.objects.get(user=user)
        return render(request,'usesr_details.html',{'user':user,'addresses':addresses ,'profile': profile})
    else :
        return redirect(signin)
    
def auto_redirect_to_google(request):
    google_app = SocialApp.objects.filter(provider='google').first()
    if google_app:
        return oauth2_login(request)
    else:
        return redirect('/') 
    
    
    
def verify_referral_code(request):
    referral_code = request.GET.get('code')
    if Profile.objects.filter(referral_code=referral_code).exists():
        request.session['valid_referral_code'] = referral_code
        return JsonResponse({'valid': True})
    return JsonResponse({'valid': False})