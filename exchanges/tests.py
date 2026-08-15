from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from exchanges.models import ExchangeRequest
from exchanges.views import send_request, accept_request, complete_request

User = get_user_model()

class ExchangeRequestTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username="alice", email="alice@example.com", password="password123")
        self.user2 = User.objects.create_user(username="bob", email="bob@example.com", password="password123")

    def _prepare_request(self, request, user):
        request.user = user
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_send_and_accept_exchange_request(self):
        # Send request
        req_post = self._prepare_request(self.factory.post('/requests/send/', {
            'receiver_username': 'bob',
            'requested_skill': 'UI/UX Design',
            'offered_skill': 'Python',
            'note': 'Let us swap skills!'
        }), self.user1)
        resp = send_request(req_post)
        self.assertEqual(resp.status_code, 302)

        req = ExchangeRequest.objects.get(sender=self.user1, receiver=self.user2)
        self.assertEqual(req.status, 'pending')

        # Accept request as Bob
        req_accept = self._prepare_request(self.factory.get(f'/requests/accept/{req.id}/'), self.user2)
        accept_resp = accept_request(req_accept, req.id)
        self.assertEqual(accept_resp.status_code, 302)

        req.refresh_from_db()
        self.assertEqual(req.status, 'accepted')

        # Complete request
        req_complete = self._prepare_request(self.factory.get(f'/requests/complete/{req.id}/'), self.user2)
        complete_resp = complete_request(req_complete, req.id)
        self.assertEqual(complete_resp.status_code, 302)

        req.refresh_from_db()
        self.assertEqual(req.status, 'completed')



