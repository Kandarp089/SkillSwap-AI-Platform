# Re-export models from dedicated modular apps for clean architecture
from notifications.models import Notification
from achievements.models import Achievement, UserAchievement
from certificates.models import Certificate
from community.models import CommunityPost, PostComment
from events.models import Event, EventRegistration

__all__ = [
    'Notification',
    'Achievement',
    'UserAchievement',
    'Certificate',
    'CommunityPost',
    'PostComment',
    'Event',
    'EventRegistration',
]
