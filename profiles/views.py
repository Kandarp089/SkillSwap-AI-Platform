from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from skills.models import Skill
from exchanges.models import ExchangeRequest

User = get_user_model()

def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User.objects.select_related('profile'), username__iexact=username)
    elif request.user.is_authenticated:
        profile_user = request.user
    else:
        return redirect('accounts:login')

    user_skills = Skill.objects.filter(user=profile_user).select_related('category')
    completed_exchanges_count = ExchangeRequest.objects.filter(
        (Q(sender=profile_user) | Q(receiver=profile_user)) & Q(status='completed')
    ).count()

    is_own_profile = (request.user == profile_user)

    return render(request, "profiles/profile.html", {
        "profile_user": profile_user,
        "profile": getattr(profile_user, 'profile', None),
        "user_skills": user_skills,
        "completed_exchanges_count": completed_exchanges_count,
        "is_own_profile": is_own_profile,
    })

@login_required(login_url='accounts:login')
def edit_profile(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        headline = request.POST.get("headline", "").strip()
        bio = request.POST.get("bio", "").strip()
        location = request.POST.get("location", "").strip()
        skills_offered = request.POST.get("skills_offered", "").strip()
        skills_wanted = request.POST.get("skills_wanted", "").strip()
        experience_level = request.POST.get("experience_level", "Intermediate")
        learning_mode = request.POST.get("learning_mode", "1-on-1 Video")
        availability = request.POST.get("availability", "").strip()
        github_url = request.POST.get("github_url", "").strip()
        linkedin_url = request.POST.get("linkedin_url", "").strip()
        website_url = request.POST.get("website_url", "").strip()

        if first_name: user.first_name = first_name
        if last_name: user.last_name = last_name
        if email: user.email = email
        user.save()

        profile.headline = headline
        profile.bio = bio
        profile.location = location
        profile.skills_offered = skills_offered
        profile.skills_wanted = skills_wanted
        profile.experience_level = experience_level
        profile.learning_mode = learning_mode
        profile.availability = availability
        profile.github_url = github_url
        profile.linkedin_url = linkedin_url
        profile.website_url = website_url

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()

        messages.success(request, "Your profile has been updated successfully!")
        return redirect("profiles:profile")

    return render(request, "profiles/edit_profile.html", {
        "profile": profile
    })