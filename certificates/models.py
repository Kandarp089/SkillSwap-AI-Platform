import uuid
from django.db import models
from django.conf import settings

def generate_cert_id():
    return f"CERT-{uuid.uuid4().hex[:10].upper()}"

class Certificate(models.Model):
    STATUS_CHOICES = (
        ('active', 'Verified & Active'),
        ('revoked', 'Revoked'),
        ('pending_approval', 'Pending Admin Approval'),
    )

    certificate_id = models.CharField(max_length=50, unique=True, default=generate_cert_id)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_certificates')
    skill_title = models.CharField(max_length=200)
    achievement_title = models.CharField(max_length=200, default="Skill Mastery Certificate")
    issued_date = models.DateField(auto_now_add=True)
    issuer = models.CharField(max_length=150, default="SkillSwap AI Peer Learning Network")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')
    verification_notes = models.TextField(blank=True, default="Verified through peer exchange completion and mentor review.")

    def __str__(self):
        return f"Cert {self.certificate_id} - {self.user.username}"

    def get_verification_url(self):
        return f"/verify/certificate/{self.certificate_id}/"
