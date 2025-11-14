from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import EmailForm, OTPVerificationForm, RegistrationForm, LoginForm
from .models import OTP

def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    step = request.session.get('register_step', 'email')
    email = request.session.get('register_email', None)
    form = None
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if step == 'email' and action == 'send_otp':
            form = EmailForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                request.session['register_email'] = email
                request.session['register_step'] = 'otp'
                OTP.generate_otp(email)
                messages.success(request, 'OTP sent to your email.')
                return redirect('register')
        
        elif step == 'otp' and action == 'verify_otp':
            form = OTPVerificationForm(request.POST, email=email)
            if form.is_valid():
                request.session['register_step'] = 'password'
                messages.success(request, 'OTP verified successfully.')
                return redirect('register')
            else:
                for error_list in form.errors.values():
                    for error in error_list:
                        messages.error(request, error)
        
        elif step == 'password' and action == 'register':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                request.session.pop('register_step', None)
                request.session.pop('register_email', None)
                messages.success(request, 'Account created successfully!')
                return redirect('profile')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
    
    # Initialize form if not already set
    if form is None:
        if step == 'email':
            form = EmailForm()
        elif step == 'otp':
            form = OTPVerificationForm(email=email)
        elif step == 'password':
            form = RegistrationForm(initial={'email': email})
    
    return render(request, 'authentication/register.html', {
        'form': form,
        'step': step,
        'email': email
    })

def send_otp_view(request):
    if request.method == 'POST':
        email = request.session.get('register_email')
        if email:
            OTP.generate_otp(email)
            messages.success(request, 'OTP resent to your email.')
        else:
            messages.error(request, 'Please enter your email first.')
    return redirect('register')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'authentication/profile.html')
