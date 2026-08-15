from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from skills.models import Skill, Category
from skills.views import browse_skills, ai_match

User = get_user_model()

class SkillModelAndViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password123")
        self.category = Category.objects.create(name="Development", slug="development", icon="bi-code")
        self.skill = Skill.objects.create(
            user=self.user,
            title="Django Web Development",
            description="Learn Django web development with python",
            category=self.category,
            level="Intermediate",
            learning_mode="1-on-1 Video",
            availability="Evenings"
        )

    def _prepare_request(self, request):
        request.user = self.user
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_skill_creation(self):
        self.assertEqual(self.skill.title, "Django Web Development")
        self.assertEqual(self.skill.category.name, "Development")

    def test_browse_skills_view(self):
        request = self._prepare_request(self.factory.get('/skills/'))
        response = browse_skills(request)
        self.assertEqual(response.status_code, 200)

    def test_ai_match_view(self):
        request = self._prepare_request(self.factory.get('/skills/ai-match/?offer_skill=python&learn_skill=uiux'))
        response = ai_match(request)
        self.assertEqual(response.status_code, 200)



