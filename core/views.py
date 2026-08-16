from django.shortcuts import render
from django.db.models import Count
from skills.models import Category, Skill
from django.contrib.auth import get_user_model
from exchanges.models import ExchangeRequest

User = get_user_model()

def home(request):
    categories = Category.objects.annotate(skill_count=Count('skills'))[:6]
    featured_skills = Skill.objects.filter(featured=True, is_active=True).select_related('user', 'category')[:6]
    top_mentors = User.objects.filter(is_verified_mentor=True).select_related('profile')[:4]
    
    total_users = User.objects.count()
    total_skills = Skill.objects.filter(is_active=True).count()
    completed_exchanges = ExchangeRequest.objects.filter(status='completed').count()

    context = {
        'categories': categories,
        'featured_skills': featured_skills,
        'top_mentors': top_mentors,
        'total_users': total_users,
        'total_skills': total_skills,
        'completed_exchanges': completed_exchanges,
    }
    return render(request, "core/index.html", context)