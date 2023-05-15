"""tests for djanog admin"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for django admin"""
    
    def setUp(self):
        """Create user and client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'admin@example.com',
            password = 'test123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'user@example.com',
            password = 'test123',
            name = 'Test User'
        )
        
    def test_users_list(self):
        """test that users are listed on page"""
        url = reverse('admin:core_user_changelist')
        result = self.client.get(url)
        
        self.assertContains(result, self.user.name)
        self.assertContains(result, self.user.email)
        
    def test_edit_user_page(self):
        """check if edit user page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        result = self.client.get(url)
        
        self.assertEqual(result.status_code, 200)
        
    def test_create_user_page(self):
        """test to check create user page"""
        url = reverse('admin:core_user_add')
        result = self.client.get(url)
        
        self.assertEqual(result.status_code, 200)