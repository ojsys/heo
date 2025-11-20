from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from .forms import CustomUserCreationForm, UserProfileForm, UserVerificationForm
from .models import User, UserVerification, EmailVerificationToken
from applications.utils import send_welcome_email, send_verification_email

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create email verification token
            verification_token = EmailVerificationToken.objects.create(user=user)

            # Send welcome email with verification link
            send_welcome_email(user, verification_token)

            # Log the user in
            login(request, user, backend='users.backends.EmailBackend')

            messages.success(
                request,
                'Registration successful! Please check your email to verify your account.'
            )
            return redirect('users:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def verify_email(request, token):
    """Verify user's email address using the token"""
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)

        if not verification_token.is_valid:
            messages.error(
                request,
                'This verification link has expired or already been used. Please request a new one.'
            )
            return redirect('users:login')

        # Mark email as verified
        user = verification_token.user
        user.is_verified = True
        user.save()

        # Mark token as used
        verification_token.mark_as_used()

        messages.success(request, 'Your email has been verified successfully!')

        # Log the user in if not already
        if not request.user.is_authenticated:
            login(request, user, backend='users.backends.EmailBackend')

        return redirect('users:profile')

    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('users:login')


def resend_verification_email(request):
    """Resend email verification link"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in first.')
        return redirect('users:login')

    if request.user.is_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('users:profile')

    # Create new verification token
    verification_token = EmailVerificationToken.objects.create(user=request.user)

    # Send verification email
    send_verification_email(request.user, verification_token)

    messages.success(request, 'Verification email sent! Please check your inbox.')
    return redirect('users:profile')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('users:profile')
    login_url = '/login/'

    def get_object(self, queryset=None):
        return self.request.user



class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:profile')
    
    def dispatch(self, *args, **kwargs):
        # Override dispatch to remove login requirement
        return super(PasswordChangeView, self).dispatch(*args, **kwargs)



@login_required
def verification_view(request):
    try:
        verification = UserVerification.objects.get(user=request.user)
    except UserVerification.DoesNotExist:
        verification = None

    if request.method == 'POST':
        form = UserVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.user = request.user
            verification.status = 'pending'
            verification.save()
            messages.success(request, 'Verification documents submitted successfully!')
            return redirect('users:profile')
    else:
        form = UserVerificationForm()

    return render(request, 'users/verification.html', {
        'form': form,
        'verification': verification
    })