from django import forms
from django.core.exceptions import ValidationError
from .models import User, OTP
from django.utils import timezone

class EmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm focus:border-orange-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-orange-500',
            'placeholder': 'you@example.com'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'sm:col-span-1 tracking-[0.6rem] text-center text-lg font-semibold text-gray-900 caret-transparent w-full rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 focus:border-orange-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-orange-500',
            'placeholder': 'Enter 6-digit code',
            'inputmode': 'numeric',
            'maxlength': '6'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.email = kwargs.pop('email', None)
        super().__init__(*args, **kwargs)
    
    def clean_otp(self):
        otp_code = self.cleaned_data.get('otp')
        if not self.email:
            raise ValidationError('Email is required.')
        
        try:
            otp_obj = OTP.objects.filter(
                email=self.email,
                is_verified=False
            ).latest('created_at')
            
            if otp_obj.expires_at < timezone.now():
                raise ValidationError('OTP has expired. Please request a new one.')
            
            if otp_obj.code != otp_code:
                raise ValidationError('Invalid OTP code.')
            
            otp_obj.is_verified = True
            otp_obj.save()
            
        except OTP.DoesNotExist:
            raise ValidationError('Invalid OTP code.')
        
        return otp_code

class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm focus:border-orange-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-orange-500',
            'readonly': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm focus:border-orange-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-orange-500',
            'placeholder': 'Create strong password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm focus:border-orange-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-orange-500',
            'placeholder': 'Re-enter password'
        })
    )
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'mt-1 h-4 w-4 rounded border-gray-300 text-orange-500 focus:ring-0 focus:ring-offset-0'
        })
    )
    
    class Meta:
        model = User
        fields = ['email']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')
            if len(password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_email_verified = True
        if commit:
            user.save()
            from .models import Profile
            Profile.objects.create(user=user)
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm focus:border-orange-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-orange-500',
            'placeholder': 'you@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm focus:border-orange-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-orange-500',
            'placeholder': 'Enter your password'
        })
    )

