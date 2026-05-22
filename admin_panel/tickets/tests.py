from django.test import TestCase, Client
from tickets.models import Venue

class DjangoServiceTests(TestCase):
    def test_healthz_endpoint(self):
        client = Client()
        response = client.get('/healthz')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_venue_creation(self):
        venue = Venue.objects.create(name="Test Venue", city="Test City")
        self.assertEqual(str(venue), "Test Venue (Test City)")

    def test_admin_login_page_loads(self):
        client = Client()
        response = client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)

    def test_database_is_reachable(self):
        self.assertEqual(Venue.objects.count(), 0)

    def test_models_exist(self):
        from tickets.models import Event, TicketTier, Reservation
        self.assertTrue(True) 