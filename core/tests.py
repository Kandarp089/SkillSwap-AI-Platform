from django.test import TestCase
from django.contrib.auth import get_user_model
from skills.models import Category, Skill
from profiles.models import UserProfile, UserSkill, WantedSkill
from exchanges.models import ExchangeRequest
from matching.services import calculate_peer_match
from certificates.models import Certificate
from exchanges.services import complete_exchange

User = get_user_model()

class SkillSwapCoreTests(TestCase):
    def setUp(self):
        # Create Super Admin
        self.admin = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='Password123!',
            role=User.Role.SUPER_ADMIN
        )
        
        # Create Mentors
        self.mentor = User.objects.create_user(
            username='mentor_test',
            email='mentor@test.com',
            password='Password123!',
            is_verified_mentor=True
        )
        self.mentor_prof = UserProfile.objects.get(user=self.mentor)
        self.mentor_prof.skills_offered = "Python Development, Django"
        self.mentor_prof.save()

        # Create Learner
        self.learner = User.objects.create_user(
            username='learner_test',
            email='learner@test.com',
            password='Password123!'
        )
        self.learner_prof = UserProfile.objects.get(user=self.learner)
        self.learner_prof.skills_wanted = "Python Development"
        self.learner_prof.save()

    def test_weighted_ai_matching_engine(self):
        score, reasons = calculate_peer_match(
            learner_user=self.learner,
            mentor_user=self.mentor,
            requested_learn_skill="Python Development",
            offered_teach_skill="UI/UX Design"
        )
        self.assertGreater(score, 70)
        self.assertTrue(len(reasons) > 0)

    def test_control_center_permissions(self):
        self.assertFalse(self.learner.has_control_panel_access())
        self.assertTrue(self.admin.has_control_panel_access())

    def test_atomic_exchange_completion_and_rewards(self):
        ex = ExchangeRequest.objects.create(
            sender=self.learner,
            receiver=self.mentor,
            requested_skill="Python Development",
            offered_skill="UI/UX Design"
        )
        # Force completion via service
        updated_ex = complete_exchange(ex.id, self.admin)
        self.assertEqual(updated_ex.status, 'completed')
        
        # Refresh profiles
        self.learner_prof.refresh_from_db()
        self.mentor_prof.refresh_from_db()
        
        self.assertEqual(self.learner_prof.xp, 1650) # 1500 default + 150
        self.assertEqual(self.mentor_prof.credits, 125) # 100 default + 25

    def test_certificate_public_model(self):
        cert = Certificate.objects.create(
            user=self.learner,
            skill_title="Python & Django Architecture",
            status="active"
        )
        self.assertTrue(cert.certificate_id.startswith("CERT-"))
        self.assertEqual(cert.status, "active")
