from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Skill, Category, SkillReview

User = get_user_model()

def seed_skills_if_empty():
    if Skill.objects.count() == 0:
        admin_user, _ = User.objects.get_or_create(username="alex_chen", email="alex@skillswap.ai")
        admin_user.set_password("SkillSwap123!")
        admin_user.first_name = "Alex"
        admin_user.last_name = "Chen"
        admin_user.save()
        if hasattr(admin_user, 'profile'):
            admin_user.profile.headline = "Senior Python Architect & ML Lead"
            admin_user.profile.skills_offered = "Python, Django, Machine Learning, Data Science"
            admin_user.profile.skills_wanted = "UI/UX Design, Figma, React"
            admin_user.profile.save()

        sarah_user, _ = User.objects.get_or_create(username="sarah_jenkins", email="sarah@skillswap.ai")
        sarah_user.set_password("SkillSwap123!")
        sarah_user.first_name = "Sarah"
        sarah_user.last_name = "Jenkins"
        sarah_user.save()
        if hasattr(sarah_user, 'profile'):
            sarah_user.profile.headline = "Lead UI/UX Designer & Product Specialist"
            sarah_user.profile.skills_offered = "UI/UX Design, Figma, Wireframing, CSS"
            sarah_user.profile.skills_wanted = "Python, Django, Web Architecture"
            sarah_user.profile.save()

        elena_user, _ = User.objects.get_or_create(username="elena_rostova", email="elena@skillswap.ai")
        elena_user.set_password("SkillSwap123!")
        elena_user.first_name = "Elena"
        elena_user.last_name = "Rostova"
        elena_user.save()
        if hasattr(elena_user, 'profile'):
            elena_user.profile.headline = "Native Spanish Educator & Cultural Mentor"
            elena_user.profile.skills_offered = "Spanish Conversation, Grammar, Translation"
            elena_user.profile.skills_wanted = "Digital Marketing, SEO, Copywriting"
            elena_user.profile.save()

        tech_cat, _ = Category.objects.get_or_create(name="Tech & Code", slug="tech", icon="bi-code-slash")
        design_cat, _ = Category.objects.get_or_create(name="Design & UI/UX", slug="design", icon="bi-palette")
        lang_cat, _ = Category.objects.get_or_create(name="Languages", slug="languages", icon="bi-translate")
        ai_cat, _ = Category.objects.get_or_create(name="AI & Machine Learning", slug="ai", icon="bi-cpu")
        music_cat, _ = Category.objects.get_or_create(name="Music & Arts", slug="music", icon="bi-music-note-beamed")

        Skill.objects.create(
            user=admin_user,
            category=tech_cat,
            title="Python & Django Web Architecture",
            description="Master full-stack Python development, Django ORM database modeling, RESTful API design, and cloud deployment pipelines.",
            level="Intermediate",
            availability="Mon-Fri Evenings",
            learning_mode="1-on-1 Video Session",
            tags="Python, Django, Backend, REST API",
            rating=4.9,
            featured=True
        )
        Skill.objects.create(
            user=sarah_user,
            category=design_cat,
            title="Figma & Modern UI/UX Design",
            description="Learn glassmorphism, responsive component libraries, wireframing, and interactive prototype systems in Figma.",
            level="Expert",
            availability="Weekends & Evenings",
            learning_mode="1-on-1 Video Session",
            tags="Figma, UI/UX, Glassmorphism, Design System",
            rating=5.0,
            featured=True
        )
        Skill.objects.create(
            user=elena_user,
            category=lang_cat,
            title="Spanish Conversational Mastery",
            description="Structured speaking sessions for intermediate and advanced learners with native accent feedback.",
            level="Beginner",
            availability="Flexible Daily",
            learning_mode="Async & Live Speaking",
            tags="Spanish, Language, Speaking, Native",
            rating=4.8,
            featured=False
        )
        Skill.objects.create(
            user=admin_user,
            category=ai_cat,
            title="Machine Learning & Deep Learning AI",
            description="Understand Neural Networks, PyTorch, Model Fine-tuning, and AI recommendation engines.",
            level="Expert",
            availability="Saturday Mornings",
            learning_mode="Group & 1-on-1",
            tags="AI, Machine Learning, PyTorch, Deep Learning",
            rating=5.0,
            featured=True
        )

def browse_skills(request):
    seed_skills_if_empty()
    skills_qs = Skill.objects.select_related('user', 'category', 'user__profile').all()

    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    level = request.GET.get('level', '').strip()
    sort_by = request.GET.get('sort', 'newest')

    if query:
        skills_qs = skills_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(user__username__icontains=query)
        )

    if category_slug and category_slug != 'all':
        skills_qs = skills_qs.filter(category__slug=category_slug)

    if level:
        skills_qs = skills_qs.filter(level=level)

    if sort_by == 'rating':
        skills_qs = skills_qs.order_by('-rating', '-created_at')
    elif sort_by == 'popular':
        skills_qs = skills_qs.order_by('-views_count', '-created_at')
    else:
        skills_qs = skills_qs.order_by('-created_at')

    categories = Category.objects.all()

    return render(request, "skills/browse_skills.html", {
        "skills": skills_qs,
        "categories": categories,
        "selected_category": category_slug,
        "selected_level": level,
        "selected_sort": sort_by,
        "query": query,
    })

@login_required(login_url='accounts:login')
def create_skill(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        level = request.POST.get("level", "Intermediate")
        category_id = request.POST.get("category")
        availability = request.POST.get("availability", "Flexible Schedule").strip()
        learning_mode = request.POST.get("learning_mode", "1-on-1 Video Session").strip()
        tags = request.POST.get("tags", "").strip()

        if not title or not description:
            messages.error(request, "Please enter both skill title and description.")
            return render(request, "skills/create_skill.html", {"categories": categories})

        category = Category.objects.filter(id=category_id).first() if category_id else None
        skill = Skill.objects.create(
            user=request.user,
            category=category,
            title=title,
            description=description,
            level=level,
            availability=availability,
            learning_mode=learning_mode,
            tags=tags
        )
        messages.success(request, f"Skill '{skill.title}' created and published successfully!")
        return redirect("skills:browse_skills")

    return render(request, "skills/create_skill.html", {"categories": categories})

def skill_detail(request, pk=None):
    seed_skills_if_empty()
    skill = None
    if pk:
        skill = Skill.objects.filter(id=pk).select_related('user', 'category', 'user__profile').first()
    if not skill:
        skill = Skill.objects.select_related('user', 'category', 'user__profile').first()
    if not skill:
        messages.info(request, "No skills available yet.")
        return redirect('skills:browse_skills')

    # Increment view count
    skill.views_count += 1
    skill.save(update_fields=['views_count'])

    # Handle Review Post
    if request.method == "POST" and request.user.is_authenticated:
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "").strip()
        if comment:
            SkillReview.objects.create(
                skill=skill,
                reviewer=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Thank you! Your review has been submitted.")
            return redirect("skills:skill_detail_pk", pk=skill.id)

    reviews = skill.reviews.select_related('reviewer').order_by('-created_at')
    related_skills = Skill.objects.filter(category=skill.category).exclude(id=skill.id)[:3]

    return render(request, "skills/skill_detail.html", {
        "skill": skill,
        "reviews": reviews,
        "related_skills": related_skills,
    })

def ai_match(request):
    from matching.services import calculate_peer_match
    
    offer_skill = request.GET.get('offer_skill', 'python').strip()
    learn_skill = request.GET.get('learn_skill', 'uiux').strip()
    exp_level = request.GET.get('experience_level', 'Intermediate')
    mode = request.GET.get('learning_mode', '1-on-1 Video')

    current_user = request.user if request.user.is_authenticated else User.objects.first()
    all_mentors = User.objects.select_related('profile').exclude(id=request.user.id if request.user.is_authenticated else 0)

    matches = []
    for mentor in all_mentors:
        prof = getattr(mentor, 'profile', None)
        score, reasons = calculate_peer_match(
            learner_user=current_user,
            mentor_user=mentor,
            requested_learn_skill=learn_skill,
            offered_teach_skill=offer_skill
        )

        matches.append({
            "mentor": mentor,
            "profile": prof,
            "score": score,
            "reasons": reasons,
            "teaches": prof.skills_offered if prof else "Various Skills",
            "wants": prof.skills_wanted if prof else "Continuous Growth",
        })

    # Sort matches by compatibility score
    matches.sort(key=lambda x: x['score'], reverse=True)

    return render(request, 'skills/ai-match.html', {
        "matches": matches[:6],
        "offer_skill": offer_skill,
        "learn_skill": learn_skill,
        "exp_level": exp_level,
        "learning_mode": mode,
    })