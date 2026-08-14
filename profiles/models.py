from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, default="Passionate peer learner and mentor on SkillSwap AI.")
    location = models.CharField(max_length=150, blank=True, default="Gujarat, India")
    skills_offered = models.CharField(max_length=300, blank=True, default="Python, Django, Web Development")
    skills_wanted = models.CharField(max_length=300, blank=True, default="UI/UX Design, Machine Learning")
    xp = models.IntegerField(default=1500)
    level = models.IntegerField(default=10)
    rating = models.FloatField(default=4.9)
    credits = models.IntegerField(default=100)

    def __str__(self):
        return f"Profile of {self.user.username}"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
