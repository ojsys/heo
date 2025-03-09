from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, UserProfileForm

User = get_user_model()

class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.register_url = reverse('users:register')
        self.profile_url = reverse('users:profile')
        self.profile_update_url = reverse('users:profile_update', kwargs={'pk': self.user.pk})

    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_register_view_post_success(self):
        data = {
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_register_view_post_invalid(self):
        data = {
            'email': 'invalid_email',
            'password1': 'pass123',
            'password2': 'different123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertFalse(User.objects.filter(email='newuser@example.com').exists())

    def test_profile_view_login_required(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next={self.profile_url}')

    def test_profile_view_get(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertIsInstance(response.context['form'], UserProfileForm)

    def test_profile_view_post_success(self):
        self.client.login(email='test@example.com', password='testpass123')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        response = self.client.post(self.profile_update_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/users/profile/')

    def test_user_update_view_login_required(self):
        response = self.client.get(self.profile_update_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next={self.profile_update_url}')

    def test_user_update_view_success(self):
        # Change from username to email
        self.client.login(email='test@example.com', password='testpass123')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        response = self.client.post(self.profile_update_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_str(self):
        self.assertEqual(str(self.user), 'test@example.com')

    def test_user_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'Test User')

    def test_user_email_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                
                email='test@example.com',  # Same email as existing user
                password='anotherpass123'
            )

class UserFormsTest(TestCase):
    def test_user_creation_form_valid(self):
        form_data = {
            'email': 'new@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_profile_form_valid(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        form = UserProfileForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())