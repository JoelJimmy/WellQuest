from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, LoginForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default goals for new user
            from wellness.models import Goal
            defaults = {
                'mental': 'Meditate daily for inner peace',
                'fitness': 'Move for 30 minutes every day',
                'nutrition': 'Stay hydrated and eat whole foods',
                'sleep': 'Get 8 quality hours every night',
            }
            for category, text in defaults.items():
                Goal.objects.create(user=user, category=category, text=text)
            login(request, user)
            messages.success(request, f'Welcome to WellQuest, {user.username}! 🎉')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')