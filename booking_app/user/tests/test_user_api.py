"""
Tests for the user API
"""
from django.test import TestCase
from django.contrib.auth import  get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """tests for unauthenticated users of the API"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_create_user_success(self):
        """test creating a user is successful"""
        payload = {
            'email':'test@example.com',
            'password': 'test1234',
            'name': 'Francisco Pages',
        }
        result = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', result.data)
        
    def test_user_with_email_exists_error(self):
        """test an error if email is already in use"""
        payload = {
            'email':'test@example.com',
            'password': 'test1234',
            'name': 'Francisco Pages',
        }
        create_user(**payload)
        result = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        
    def password_too_short_error(self):
        """test an error if password is less than 8 characters"""
        payload = {
            'email':'test@example.com',
            'password': '1234567',
            'name': 'Francisco Pages',
        }
        
        result = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
        
    