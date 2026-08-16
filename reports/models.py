from django.db import models
from django.conf import settings

class ContentReport(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved / Action Taken'),
        ('dismissed', 'Dismissed'),
    )
    TARGET_CHOICES = (
        ('user', 'User Profile'),
        ('skill', 'Skill Listing'),
        ('post', 'Community Post'),
        ('message', 'Chat Message'),
        ('review', 'Review'),
        ('exchange', 'Exchange Dispute'),
    )

    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_reports')
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)
    target_id = models.CharField(max_length=100)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    resolution_notes = models.TextField(blank=True, default='')
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report #{self.id} on {self.target_type}:{self.target_id} ({self.status})"
