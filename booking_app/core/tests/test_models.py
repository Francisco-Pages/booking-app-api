"""
Tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTest(TestCase):
    """Test models."""
    
    def test_create_user_email_successful(self):
        """test creating a user with an email"""
        email = 'test_email@example.com'
        password = 'test_password123'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_new_user_email_normalized(self):
        """test if user's email is normalized"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
            
        ]
        for test_email, expected in sample_emails:
            user = get_user_model().objects.create_user(test_email, 'sample123')
            self.assertEqual(user.email, expected)
            
    def test_new_user_without_email_raises_error(self):
        """raises an exception if user does not provide a value"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','test123')
            
    def test_create_superuser(self):
        """test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
    def test_create_rental_unit(self):
        """test creating a listing is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'test123'
        )
        rental_unit = models.RentalUnit.objects.create(
            user=user,
            title='test unit name',
            description='new home for rent - testing',
            link='https://www.rental-unit.com/',
            languages='fra',
            status='inactive',
            images='images of don pedro',
            unit_type='apartment',
            max_guests=6,
        )
        
        self.assertEqual(str(rental_unit), rental_unit.title)