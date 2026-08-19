from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def login_view(request):

    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        print("========== LOGIN DEBUG ==========")
        print("USERNAME =", username)
        print("PASSWORD =", password)

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print("AUTH RESULT =", user)
        print("=================================")

        if user is not None:
            login(request, user)
            return redirect('/dashboard/')

        messages.error(
            request,
            'Invalid username or password'
        )

    return render(request, 'accounts/login.html')


def register_view(request):

    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('/accounts/register/')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('/accounts/register/')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('/accounts/register/')

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(
            request,
            'Registration successful! Please login.'
        )

        return redirect('/accounts/login/')

    return render(request, 'accounts/register.html')


def logout_view(request):
    logout(request)
    return redirect('/')