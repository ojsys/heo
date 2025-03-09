from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Category, Page, Media, ImpactStory, Announcement

User = get_user_model()

class CMSViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True
        )
        self.page = Page.objects.create(
            title='Test Page',
            content='Test Content',
            created_by=self.user,
            is_published=True
        )

    def test_page_list_view(self):
        response = self.client.get(reverse('cms:page_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms/page_list.html')
        self.assertContains(response, 'Test Page')

    def test_page_detail_view(self):
        response = self.client.get(reverse('cms:page_detail', kwargs={'slug': self.page.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms/page_detail.html')

class APITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123',
            is_staff=True
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.page = Page.objects.create(
            title='API Test Page',
            content='API Test Content',
            created_by=self.user,
            category=self.category
        )

    def test_category_list(self):
        response = self.client.get('/cms/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        categories = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(categories), 1)

    def test_page_crud(self):
        # Test authentication
        self.client.force_authenticate(user=self.user)

        # Test create
        page_data = {
            'title': 'New Test Page',
            'content': 'New Test Content',
            'status': 'draft',
            'slug': 'new-test-page',  # Add required field
            'meta_description': 'Test meta description'  # Add required field
        }
        response = self.client.post('/cms/api/pages/', page_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test read
        response = self.client.get(f'/cms/api/pages/{self.page.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Test Page')

        # Test update
        update_data = {'title': 'Updated Page'}
        response = self.client.patch(f'/cms/api/pages/{self.page.slug}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Page')

    def test_page_publish(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/cms/api/pages/{self.page.slug}/publish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.page.refresh_from_db()
        self.assertTrue(self.page.is_published)

    def test_page_versions(self):
        self.client.force_authenticate(user=self.user)
        self.page.create_version(user=self.user, comment='Initial version')
        response = self.client.get(f'/cms/api/pages/{self.page.slug}/versions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)