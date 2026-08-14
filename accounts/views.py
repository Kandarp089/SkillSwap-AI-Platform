from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        username_input = request.POST.get("username", "").strip()
        password_input = request.POST.get("password", "")

        if not username_input or not password_input:
            messages.error(request, "Please enter both username/email and password.")
            return render(request, "accounts/login.html")

        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("dashboard:home")
        else:
            messages.error(request, "Invalid email/username or password. Please try again.")

    return render(request, "accounts/login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password1:
            messages.error(request, "Please fill out all required registration fields.")
            return render(request, "accounts/register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match. Please re-enter passwords.")
            return render(request, "accounts/register.html")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "That username is already taken. Please choose another.")
            return render(request, "accounts/register.html")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with that email already exists. Please log in.")
            return render(request, "accounts/register.html")

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            
            # Authenticate & Login newly created user
            authenticated_user = authenticate(request, username=username, password=password1)
            if authenticated_user:
                login(request, authenticated_user)
            
            messages.success(request, f"Account created successfully! Welcome to SkillSwap AI, {username}!")
            return redirect("dashboard:home")
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")

    return render(request, "accounts/register.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("/")