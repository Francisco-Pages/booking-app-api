"""
Tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_superuser(**params):
    """create and return a new user"""
    return get_user_model().objects.create_superuser(**params)

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
        
    def test_create_amenities_list(self):
        """test creating an amenities list for a rental unit is successful"""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with amenities")
        
        amenities_list = models.AmenitiesList.objects.create(rental_unit=rental_unit)
        
        self.assertTrue(models.AmenitiesList.objects.filter(rental_unit=amenities_list.rental_unit).exists())
        
    def test_create_location(self):
        """test creating a location for a rental unit is successful"""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with a location")
        
        location = models.Location.objects.create(rental_unit=rental_unit)
        
        self.assertTrue(models.Location.objects.filter(rental_unit=location.rental_unit).exists())
        
    def test_create_room_or_space(self):
        """test creating a room or space for a rental unit is successful"""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with a location")
        
        room_or_space = models.RoomOrSpace.objects.create(rental_unit=rental_unit)
        
        self.assertTrue(models.RoomOrSpace.objects.filter(rental_unit=room_or_space.rental_unit).exists())