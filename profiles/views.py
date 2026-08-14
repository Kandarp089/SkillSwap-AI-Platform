from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def profile_view(request):
    return render(request, "profiles/profile.html")

@login_required(login_url='accounts:login')
def edit_profile(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        user = request.user
        if first_name: user.first_name = first_name
        if last_name: user.last_name = last_name
        if email: user.email = email
        user.save()

        messages.success(request, "Your profile has been updated successfully!")
        return redirect("profiles:profile")

    return render(request, "profiles/edit_profile.html")