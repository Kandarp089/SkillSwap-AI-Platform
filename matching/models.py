from django.db import models
from django.conf import settings

class AIMatchWeight(models.Model):
    name = models.CharField(max_length=100, default="Production AI Matching Weights")
    skill_overlap_weight = models.IntegerField(default=35, help_text="Weight for exact skill match (%)")
    wanted_offered_weight = models.IntegerField(default=25, help_text="Weight for wanted/offered compatibility (%)")
    experience_weight = models.IntegerField(default=10, help_text="Weight for experience compatibility (%)")
    availability_weight = models.IntegerField(default=10, help_text="Weight for availability overlap (%)")
    learning_mode_weight = models.IntegerField(default=5, help_text="Weight for learning mode preference (%)")
    language_weight = models.IntegerField(default=5, help_text="Weight for language preference (%)")
    rating_weight = models.IntegerField(default=5, help_text="Weight for reputation rating (%)")
    activity_weight = models.IntegerField(default=5, help_text="Weight for active platform engagement (%)")
    updated_at = models.DateTimeField(auto_now=True)

    def total_weight(self):
        return (self.skill_overlap_weight + self.wanted_offered_weight + 
                self.experience_weight + self.availability_weight + 
                self.learning_mode_weight + self.language_weight + 
                self.rating_weight + self.activity_weight)

    def __str__(self):
        return f"{self.name} (Total: {self.total_weight()}%)"


class AIMatch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_matches_as_learner')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_matches_as_mentor')
    score = models.IntegerField(default=85)
    reasons_json = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'mentor')
        ordering = ['-score']

    def __str__(self):
        return f"Match: {self.user.username} <-> {self.mentor.username} ({self.score}%)"
