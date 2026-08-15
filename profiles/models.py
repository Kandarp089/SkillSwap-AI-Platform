from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    bio = models.TextField(blank=True, default="Passionate peer learner and mentor on SkillSwap AI.")
    location = models.CharField(max_length=150, blank=True, default="Gujarat, India")
    skills_offered = models.CharField(max_length=500, blank=True, default="Python, Django, Web Development")
    skills_wanted = models.CharField(max_length=500, blank=True, default="UI/UX Design, Machine Learning")
    experience_level = models.CharField(max_length=30, choices=EXPERIENCE_CHOICES, default='Intermediate')
    learning_mode = models.CharField(max_length=30, choices=MODE_CHOICES, default='1-on-1 Video')
    availability = models.CharField(max_length=100, blank=True, default="Evenings & Weekends")
    xp = models.IntegerField(default=1500)
    level = models.IntegerField(default=10)
    rating = models.FloatField(default=4.9)
    credits = models.IntegerField(default=100)
    github_url = models.URLField(blank=True, max_length=300)
    linkedin_url = models.URLField(blank=True, max_length=300)
    website_url = models.URLField(blank=True, max_length=300)

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def skills_offered_list(self):
        if not self.skills_offered:
            return []
        return [s.strip() for s in self.skills_offered.split(',') if s.strip()]

    @property
    def skills_wanted_list(self):
        if not self.skills_wanted:
            return []
        return [s.strip() for s in self.skills_wanted.split(',') if s.strip()]

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

