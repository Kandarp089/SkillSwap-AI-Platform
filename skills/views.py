from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Skill, Category

User = get_user_model()

def seed_skills_if_empty():
    if Skill.objects.count() == 0:
        admin_user, _ = User.objects.get_or_create(username="alex_chen", email="alex@skillswap.ai")
        admin_user.set_password("SkillSwap123!")
        admin_user.save()

        sarah_user, _ = User.objects.get_or_create(username="sarah_jenkins", email="sarah@skillswap.ai")
        sarah_user.set_password("SkillSwap123!")
        sarah_user.save()

        elena_user, _ = User.objects.get_or_create(username="elena_rostova", email="elena@skillswap.ai")
        elena_user.set_password("SkillSwap123!")
        elena_user.save()

        tech_cat, _ = Category.objects.get_or_create(name="Tech & Code", slug="tech", icon="bi-code-slash")
        design_cat, _ = Category.objects.get_or_create(name="Design & UI/UX", slug="design", icon="bi-palette")
        lang_cat, _ = Category.objects.get_or_create(name="Languages", slug="languages", icon="bi-translate")
        ai_cat, _ = Category.objects.get_or_create(name="AI & Machine Learning", slug="ai", icon="bi-cpu")

        Skill.objects.create(
            user=admin_user,
            category=tech_cat,
            title="Python & Django Web Architecture",
            description="Master full-stack Python development, Django ORM database modeling, RESTful API design, and cloud deployment pipelines.",
            level="Intermediate",
            rating=4.9
        )
        Skill.objects.create(
            user=sarah_user,
            category=design_cat,
            title="Figma & Modern UI/UX Design",
            description="Learn glassmorphism, responsive component libraries, wireframing, and interactive prototype systems in Figma.",
            level="Expert",
            rating=5.0
        )
        Skill.objects.create(
            user=elena_user,
            category=lang_cat,
            title="Spanish Conversational Mastery",
            description="Structured speaking sessions for intermediate and advanced learners with native accent feedback.",
            level="Beginner",
            rating=4.8
        )
        Skill.objects.create(
            user=admin_user,
            category=ai_cat,
            title="Machine Learning & Deep Learning AI",
            description="Understand Neural Networks, PyTorch, Model Fine-tuning, and AI recommendation engines.",
            level="Expert",
            rating=5.0
        )

def browse_skills(request):
    seed_skills_if_empty()
    skills = Skill.objects.all().select_related('user', 'category').order_by('-created_at')
    categories = Category.objects.all()
    return render(request, "skills/browse_skills.html", {
        "skills": skills,
        "categories": categories
    })

@login_required(login_url='accounts:login')
def create_skill(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        level = request.POST.get("level", "Intermediate")
        category_id = request.POST.get("category")

        if not title or not description:
            messages.error(request, "Please enter skill title and description.")
            return render(request, "skills/create_skill.html", {"categories": Category.objects.all()})

        category = Category.objects.filter(id=category_id).first() if category_id else None
        skill = Skill.objects.create(
            user=request.user,
            category=category,
            title=title,
            description=description,
            level=level
        )
        messages.success(request, f"Skill '{skill.title}' created and published successfully!")
        return redirect("skills:browse_skills")

    return render(request, "skills/create_skill.html", {"categories": Category.objects.all()})

def skill_detail(request, pk=None):
    seed_skills_if_empty()
    skill = Skill.objects.first()
    if pk:
        skill = get_object_or_404(Skill, id=pk)
    return render(request, "skills/skill_detail.html", {"skill": skill})

def ai_match(request):
    seed_skills_if_empty()
    return render(request, 'skills/ai-match.html')