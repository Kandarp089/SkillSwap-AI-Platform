from django.shortcuts import render

def profile_view(request):
    return render(
        request,
        "profiles/profile.html"
    )

def edit_profile(request):
    return render(
        request,
        "profiles/edit_profile.html"
    )