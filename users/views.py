from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from .forms import CustomUserCreationForm, UserProfileForm, UserVerificationForm
from .models import User, UserVerification

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='users.backends.EmailBackend')
            messages.success(request, 'Registration successful!')
            return redirect('users:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

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