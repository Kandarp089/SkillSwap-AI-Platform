from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from skills.models import Category, Skill
from profiles.models import UserProfile, UserSkill, WantedSkill
from exchanges.models import ExchangeRequest, XPLedger, CreditTransaction
from certificates.models import Certificate
from community.models import CommunityPost
from events.models import Event, EventRegistration
from achievements.models import Achievement, UserAchievement
from matching.models import AIMatchWeight

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with production demo users, mentors, skills, categories, exchanges, achievements, and events."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting database seeding process..."))

        # 1. Ensure Super Admin / Control Center Admin user exists
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@skillswap.ai",
                "first_name": "Control",
                "last_name": "Center Admin",
                "is_staff": True,
                "is_superuser": True,
                "role": User.Role.SUPER_ADMIN,
                "is_verified_mentor": True
            }
        )
        if created or not admin_user.check_password("SkillSwap123!"):
            admin_user.set_password("SkillSwap123!")
            admin_user.role = User.Role.SUPER_ADMIN
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user)
        self.stdout.write(self.style.SUCCESS(f"Super Admin ready: @{admin_user.username} (Password: SkillSwap123!)"))

        # 2. Seed AI Matching Weights
        weights, _ = AIMatchWeight.objects.get_or_create(id=1)

        # 3. Seed Categories
        cat_tech, _ = Category.objects.get_or_create(name="Tech & Code", defaults={"slug": "tech", "icon": "bi-code-slash", "description": "Software, web architecture, and full-stack engineering."})
        cat_design, _ = Category.objects.get_or_create(name="Design & UI/UX", defaults={"slug": "design", "icon": "bi-palette", "description": "Product design, Figma, UI glassmorphism, and design systems."})
        cat_ai, _ = Category.objects.get_or_create(name="AI & Machine Learning", defaults={"slug": "ai", "icon": "bi-cpu", "description": "Deep learning, Neural Networks, PyTorch, and NLP."})
        cat_lang, _ = Category.objects.get_or_create(name="Languages", defaults={"slug": "languages", "icon": "bi-translate", "description": "Conversational practice, fluency, and translation."})

        # 4. Seed Mentors & Learners
        alex, _ = User.objects.get_or_create(username="alex_chen", defaults={"email": "alex@skillswap.ai", "first_name": "Alex", "last_name": "Chen", "is_verified_mentor": True})
        alex.set_password("SkillSwap123!")
        alex.save()
        alex_prof, _ = UserProfile.objects.get_or_create(user=alex)
        alex_prof.headline = "Senior Python Architect & ML Lead"
        alex_prof.bio = "10+ years developing scalable Python backends, Django microservices, and AI models."
        alex_prof.location = "California, USA"
        alex_prof.xp = 3200
        alex_prof.level = 21
        alex_prof.skills_offered = "Python Development, Django Architecture, Machine Learning"
        alex_prof.skills_wanted = "UI/UX Design, Figma"
        alex_prof.save()

        sarah, _ = User.objects.get_or_create(username="sarah_jenkins", defaults={"email": "sarah@skillswap.ai", "first_name": "Sarah", "last_name": "Jenkins", "is_verified_mentor": True})
        sarah.set_password("SkillSwap123!")
        sarah.save()
        sarah_prof, _ = UserProfile.objects.get_or_create(user=sarah)
        sarah_prof.headline = "Lead UI/UX Designer & Design Systems Spec"
        sarah_prof.bio = "Designing interactive glassmorphism UI, Figma wireframes, and design components."
        sarah_prof.location = "London, UK"
        sarah_prof.xp = 2800
        sarah_prof.level = 18
        sarah_prof.skills_offered = "UI/UX Design, Figma Prototyping, CSS"
        sarah_prof.skills_wanted = "Python Development"
        sarah_prof.save()

        demo_user, _ = User.objects.get_or_create(username="demo_user", defaults={"email": "learner@skillswap.ai", "first_name": "Demo", "last_name": "Learner"})
        demo_user.set_password("SkillSwap123!")
        demo_user.save()
        demo_prof, _ = UserProfile.objects.get_or_create(user=demo_user)
        demo_prof.headline = "Full-Stack Aspirant & Tech Enthusiast"
        demo_prof.xp = 1600
        demo_prof.level = 10
        demo_prof.save()

        # 5. Seed Skills
        s1, _ = Skill.objects.get_or_create(
            title="Python & Django Web Architecture",
            defaults={
                "user": alex,
                "category": cat_tech,
                "description": "Master full-stack Python development, Django ORM database modeling, RESTful API design, and cloud deployment pipelines.",
                "level": "Intermediate",
                "featured": True
            }
        )

        s2, _ = Skill.objects.get_or_create(
            title="Figma & Modern UI/UX Design",
            defaults={
                "user": sarah,
                "category": cat_design,
                "description": "Learn glassmorphism, responsive component libraries, wireframing, and interactive prototype systems in Figma.",
                "level": "Expert",
                "featured": True
            }
        )

        # 6. Seed Relational UserSkill & WantedSkill
        UserSkill.objects.get_or_create(user=alex, skill=s1, defaults={"proficiency": "Expert"})
        WantedSkill.objects.get_or_create(user=alex, skill=s2, defaults={"priority": "High"})
        UserSkill.objects.get_or_create(user=sarah, skill=s2, defaults={"proficiency": "Expert"})
        WantedSkill.objects.get_or_create(user=sarah, skill=s1, defaults={"priority": "High"})

        # 7. Seed Verified Completed Exchanges
        ex1, ex1_created = ExchangeRequest.objects.get_or_create(
            sender=demo_user,
            receiver=alex,
            requested_skill="Python Development",
            defaults={
                "offered_skill": "UI/UX Design",
                "status": "completed",
                "rating": 5,
                "feedback": "Outstanding mentorship session! Alex explained Django ORM optimization exceptionally well.",
                "sender_confirmed": True,
                "receiver_confirmed": True,
                "completed_at": timezone.now()
            }
        )

        # 8. Seed Verified Certificate
        cert, _ = Certificate.objects.get_or_create(
            user=demo_user,
            skill_title="Python & Django Web Architecture",
            defaults={
                "achievement_title": "Verified Peer Skill Mastery",
                "status": "active",
                "verification_notes": "Completed 1-on-1 mentorship session with @alex_chen and earned positive review."
            }
        )

        # 9. Seed Achievements
        ach1, _ = Achievement.objects.get_or_create(
            title="First Skill Exchange",
            defaults={"description": "Successfully completed your first peer skill exchange.", "icon": "bi-award-fill", "xp_reward": 100}
        )
        UserAchievement.objects.get_or_create(user=demo_user, achievement=ach1)

        # 10. Seed Events
        ev1, _ = Event.objects.get_or_create(
            title="Live AI Skill Swap & Architecture Workshop 2026",
            defaults={
                "description": "Interactive live stream on peer-to-peer learning, Django Channels WebSocket integration, and AI matching algorithms.",
                "organizer": alex,
                "event_date": timezone.now() + timezone.timedelta(days=7),
                "location_type": "Online Live Stream",
                "meet_url": "https://meet.jit.si/SkillSwapAIWorkshop"
            }
        )
        EventRegistration.objects.get_or_create(event=ev1, user=demo_user)

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully! All demo users, mentors, skills, certificates, and events are ready."))
