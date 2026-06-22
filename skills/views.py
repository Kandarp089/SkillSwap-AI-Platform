from django.shortcuts import render

def browse_skills(request):
    return render(
        request,
        "skills/browse_skills.html"
    )

def skill_detail(request):
    return render(
        request,
        "skills/skill_detail.html"
    )

def ai_match(request):
    return render(
        request,
        'skills/ai-match.html'
    )