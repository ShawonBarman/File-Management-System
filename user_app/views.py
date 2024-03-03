from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout as user_logout  # Rename logout function to avoid conflicts

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')

        if password != repassword:
            messages.success(request, 'Passwords do not match.')
            return redirect('signup')

        exists_user = User.objects.filter(username=username)
        if exists_user:
            messages.success(request, 'Username is already taken.')
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Registration successful. You can now log in.')
        return redirect('signin')
    else:
        return render(request, 'register.html')

def user_login(request):  # Renamed login function to user_login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('home')
        else:
            messages.success(request, 'Invalid username or password.')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

def logout(request):
    user_logout(request)  # Call the renamed logout function
    return redirect('signin')
