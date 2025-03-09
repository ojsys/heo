from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Program, Application, ApplicationDocument, NotificationPreference
from datetime import datetime, timedelta

User = get_user_model()

class ApplicationViewTests(TestCase):
    def setUp(self):
        # Create test users
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        # Create test program
        self.program = Program.objects.create(
            name='Test Program',
            program_type='scholarship',
            description='Test Description',
            eligibility_criteria='Test Criteria',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True
        )
        
        # Create test application
        self.application = Application.objects.create(
            program=self.program,
            applicant=self.user,
            form_data={'test_field': 'test_value'},
            status='submitted',
            submitted_at=timezone.now()
        )

    def test_program_list_view(self):
        response = self.client.get(reverse('applications:program_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications/program_list.html')
        self.assertContains(response, 'Test Program')

    def test_program_detail_view(self):
        response = self.client.get(reverse('applications:program_detail', kwargs={'pk': self.program.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications/program_detail.html')
        self.assertContains(response, self.program.name)

    def test_application_create_view(self):
        # Login required test
        response = self.client.get(reverse('applications:application_create', kwargs={'program_id': self.program.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to login

        # Successful login and access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('applications:application_create', kwargs={'program_id': self.program.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications/application_form.html')

    def test_application_detail_view(self):
        # Login required test
        response = self.client.get(reverse('applications:application_detail', kwargs={'pk': self.application.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to login

        # Test access by application owner
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('applications:application_detail', kwargs={'pk': self.application.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications/application_detail.html')

        # Test access by staff
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(reverse('applications:application_detail', kwargs={'pk': self.application.pk}))
        self.assertEqual(response.status_code, 200)

    def test_application_review(self):
        review_url = reverse('applications:application_review', kwargs={'pk': self.application.pk})
        
        # Test access denied for non-staff
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(review_url)
        self.assertEqual(response.status_code, 302)  # Redirects to program list

        # Test access granted for staff
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(review_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications/application_review.html')

    def test_dashboard_view(self):
        dashboard_url = reverse('applications:dashboard')
        
        # Test access denied for non-staff
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Test access granted for staff
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications/dashboard.html')

    def test_export_applications(self):
        export_url = reverse('applications:export_applications')
        
        # Test access denied for non-staff
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(export_url)
        self.assertEqual(response.status_code, 302)  # Redirects

        # Test CSV export for staff
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(export_url, {'format': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

        # Test Excel export
        response = self.client.get(export_url, {'format': 'excel'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Test PDF export
        response = self.client.get(export_url, {'format': 'pdf'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_bulk_application_review(self):
        bulk_review_url = reverse('applications:bulk_application_review')
        
        # Test access denied for non-staff
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(bulk_review_url)
        self.assertEqual(response.status_code, 302)  # Redirects

        # Test bulk approve for staff
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.post(bulk_review_url, {
            'application_ids': [self.application.id],
            'action': 'approve'
        })
        self.assertEqual(response.status_code, 302)  # Redirects to application list
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'approved')

    def test_notification_preferences(self):
        prefs_url = reverse('applications:notification_preferences')
        
        # Test login required
        response = self.client.get(prefs_url)
        self.assertEqual(response.status_code, 302)  # Redirects to login

        # Test GET request
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(prefs_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications/notification_preferences.html')

        # Test POST request
        response = self.client.post(prefs_url, {
            'email_on_status_change': 'on',
            'email_on_review': 'on',
            'email_on_document_request': 'off'
        })
        self.assertEqual(response.status_code, 200)
        pref = NotificationPreference.objects.get(user=self.user)
        self.assertTrue(pref.email_on_status_change)
        self.assertTrue(pref.email_on_review)
        self.assertFalse(pref.email_on_document_request)

    def test_analytics_view(self):
        analytics_url = reverse('applications:analytics')
        
        # Test access denied for non-staff
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(analytics_url)
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Test access granted for staff
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(analytics_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications/analytics.html')

        # Test context data
        self.assertIn('monthly_applications', response.context)
        self.assertIn('program_success_rates', response.context)
        self.assertIn('avg_processing_time', response.context)