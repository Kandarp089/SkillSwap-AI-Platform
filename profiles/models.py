from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

class UserProfile(models.Model):
    EXPERIENCE_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    )

    MODE_CHOICES = (
        ('1-on-1 Video', '1-on-1 Video'),
        ('Async Chat', 'Async Chat'),
        ('Group Session', 'Group Session'),
        ('Flexible', 'Flexible'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    headline = models.CharField(max_length=200, blank=True, default="Peer Learner & Mentor")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    bio = models.TextField(blank=True, default="Passionate peer learner and mentor on SkillSwap AI.")
    location = models.CharField(max_length=150, blank=True, default="Gujarat, India")
    experience_level = models.CharField(max_length=30, choices=EXPERIENCE_CHOICES, default='Intermediate')
    learning_mode = models.CharField(max_length=30, choices=MODE_CHOICES, default='1-on-1 Video')
    availability = models.CharField(max_length=100, blank=True, default="Evenings & Weekends")
    xp = models.PositiveIntegerField(default=1500)
    level = models.PositiveIntegerField(default=10)
    credits = models.IntegerField(default=100)
    github_url = models.URLField(blank=True, max_length=300)
    linkedin_url = models.URLField(blank=True, max_length=300)
    website_url = models.URLField(blank=True, max_length=300)
    
    # Deprecated fallback fields maintained for backwards compatibility
    skills_offered = models.CharField(max_length=500, blank=True, default="Python, Django, Web Development")
    skills_wanted = models.CharField(max_length=500, blank=True, default="UI/UX Design, Machine Learning")

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def rating(self):
        from exchanges.models import ExchangeRequest
        avg_rating = ExchangeRequest.objects.filter(
            receiver=self.user,
            status='completed',
            rating__isnull=False
        ).aggregate(Avg('rating'))['rating__avg'] if hasattr(ExchangeRequest.objects, 'aggregate') else None
        
        # Calculate real rating or return standard default based on completed exchanges
        completed_exchanges = ExchangeRequest.objects.filter(
            models.Q(sender=self.user) | models.Q(receiver=self.user),
            status='completed'
        ).count() if hasattr(self.user, 'sent_requests') else 0
        
        if avg_rating:
            return round(float(avg_rating), 1)
        return 4.9 if completed_exchanges > 0 else 5.0

    @property
    def completed_exchanges_count(self):
        from exchanges.models import ExchangeRequest
        return ExchangeRequest.objects.filter(
            models.Q(sender=self.user) | models.Q(receiver=self.user),
            status='completed'
        ).count()

    @property
    def skills_offered_list(self):
        skills = list(self.user.skills_offered_rel.values_list('skill__title', flat=True))
        if skills:
            return skills
        if not self.skills_offered:
            return []
        return [s.strip() for s in self.skills_offered.split(',') if s.strip()]

    @property
    def skills_wanted_list(self):
        skills = list(self.user.skills_wanted_rel.values_list('skill__title', flat=True))
        if skills:
            return skills
        if not self.skills_wanted:
            return []
        return [s.strip() for s in self.skills_wanted.split(',') if s.strip()]

    def calculate_level(self):
        # 100 XP = 1 Level
        self.level = max(1, self.xp // 150)
        return self.level


class UserSkill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skills_offered_rel')
    skill = models.ForeignKey('skills.Skill', on_delete=models.CASCADE, related_name='offered_by_users')
    proficiency = models.CharField(max_length=20, choices=UserProfile.EXPERIENCE_CHOICES, default='Intermediate')
    years_experience = models.PositiveIntegerField(default=1)
    availability = models.CharField(max_length=100, default='Evenings & Weekends')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username} teaches {self.skill.title}"


class WantedSkill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skills_wanted_rel')
    skill = models.ForeignKey('skills.Skill', on_delete=models.CASCADE, related_name='wanted_by_users')
    priority = models.CharField(max_length=20, choices=(('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')), default='High')
    target_level = models.CharField(max_length=20, choices=UserProfile.EXPERIENCE_CHOICES, default='Advanced')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username} wants to learn {self.skill.title}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
