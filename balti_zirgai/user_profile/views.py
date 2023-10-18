from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.http import HttpRequest
from . import models, forms

User = get_user_model()

@csrf_protect
def profile_update(request: HttpRequest):
    try:
        user_profile = request.user.profile
    except models.Profile.DoesNotExist:
        user_profile = None
    if request.method == "POST":
        user_form = forms.UserUpdateForm(request.POST, instance=request.user)
        if user_profile is not None:
            profile_form = forms.ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        else:
            profile_form = forms.ProfileUpdateForm(request.POST, request.FILES)
            profile_form.instance.user = request.user
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your user profile changes have been saved.')
            return redirect('profile')
    else:
        user_form = forms.UserUpdateForm(instance=request.user)
        if user_profile is not None:
            profile_form = forms.ProfileUpdateForm(instance=user_profile)
        else:
            profile_form = forms.ProfileUpdateForm()
            profile_form.instance.user = request.user

    return render(request, 'user_profile/update.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def profile(request: HttpRequest):
    user = request.user
    context = {'user': user}
    return render(request, "user_profile/profile.html", context)

@csrf_protect
def signup(request: HttpRequest):
    if request.method == "POST":
        errors = []
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not len(username) > 4 or User.objects.filter(username=username).exists():
            errors.append('Username is already taken, or is too short.')
        if not len(email) > 0 or User.objects.filter(email=email).exists():
            errors.append('Email must be valid and not belonging to an existing user.')
        if not len(password1) > 7 or password1 != password2:
            errors.append('Password is too short, or entered passwords do not match.')
        if len(errors):
            for error in errors:
                messages.error(request, error)
        else:
            User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, "Sign up successful. You can log in now.")
            return redirect('login')
    return render(request, 'user_profile/signup.html')

def profile_view(request):
    user = request.user 
    return render(request, 'profile_template.html', {'user': user})
