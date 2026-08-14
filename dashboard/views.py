from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def dashboard_home(request):
    return render(request, 'dashboard/dashboard.html')

def leaderboard(request):
    return render(request, 'dashboard/leaderboard.html')

def notifications(request):
    return render(request, "dashboard/notifications.html")

def settings_page(request):
    return render(request, "dashboard/settings.html")

def achievements(request):
    return render(request, "dashboard/achievements.html")

def certificates(request):
    return render(request, "dashboard/certificates.html")

def community(request):
    return render(request, 'dashboard/community.html')

def events(request):
    return render(request, 'dashboard/events.html')

def about(request):
    return render(request, 'dashboard/about.html')

def contact(request):
    return render(request, 'dashboard/contact.html')

def help_center(request):
    return render(request, 'dashboard/help_center.html')

def blog(request):
    return render(request, 'dashboard/blog.html')

def careers(request):
    return render(request, 'dashboard/careers.html')

def privacy_policy(request):
    return render(request, 'dashboard/privacy_policy.html')

def terms_of_use(request):
    return render(request, 'dashboard/terms_of_use.html')

def cookies_policy(request):
    return render(request, 'dashboard/cookies_policy.html')

def accessibility(request):
    return render(request, 'dashboard/accessibility.html')