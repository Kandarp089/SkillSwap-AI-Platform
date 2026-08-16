from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        ADMIN = 'ADMIN', 'Admin'
        MODERATOR = 'MODERATOR', 'Moderator'
        SUPPORT = 'SUPPORT', 'Support Agent'
        CONTENT_MANAGER = 'CONTENT_MANAGER', 'Content Manager'
        ANALYTICS_MANAGER = 'ANALYTICS_MANAGER', 'Analytics Manager'
        USER = 'USER', 'Standard User'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.USER)
    is_verified_mentor = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspension_reason = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_or_staff(self):
        return self.is_superuser or self.is_staff or self.role in [
            self.Role.SUPER_ADMIN, self.Role.ADMIN, self.Role.MODERATOR,
            self.Role.SUPPORT, self.Role.CONTENT_MANAGER, self.Role.ANALYTICS_MANAGER
        ]

    def has_control_panel_access(self):
        return self.is_admin_or_staff and not self.is_suspended