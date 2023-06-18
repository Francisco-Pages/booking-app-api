"""
Tests for models
"""
from datetime import datetime, date, timezone, timedelta

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

now = datetime.now().date()

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
            status=False,
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
        
    def test_create_room(self):
        """test creating a room for a rental unit is successful"""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with a location")
        
        room = models.Room.objects.create(rental_unit=rental_unit)
        
        self.assertTrue(models.Room.objects.filter(rental_unit=room.rental_unit).exists())
        
    def test_create_pricing(self):
        """test creating a pricing list for a rental unit is successful"""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with a location")
        
        pricing = models.Pricing.objects.create(rental_unit=rental_unit)
        
        self.assertTrue(models.Pricing.objects.filter(rental_unit=pricing.rental_unit).exists())
        
    def test_create_fee(self):
        """Test creating a fee is successful."""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with a location")
    
        fee = models.Fee.objects.create(rental_unit=rental_unit)
        
        self.assertTrue(models.Fee.objects.filter(id=fee.id).exists())
        
    def test_create_availability(self):
        """Test creating availability preference for a rental unit is successful."""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with availability preferences")
        
        availability = models.Availability.objects.create(rental_unit=rental_unit)
        
        self.assertTrue(models.Availability.objects.filter(rental_unit=availability.rental_unit).exists())
        
    def test_create_calendar_event(self):
        """Test creating calendar event for a rental unit is successful."""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with availability preferences")
        
        calendar_event = models.CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason='Reserved'
        )

        self.assertTrue(models.CalendarEvent.objects.filter(id=calendar_event.id).exists())
        
        
    def test_create_rulebook(self):
        """test creating the rulebook for a rental unit"""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with availability preferences")
        
        rulebook = models.Rulebook.objects.create(rental_unit=rental_unit)
        
        self.assertTrue(models.Rulebook.objects.filter(rental_unit=rulebook.rental_unit).exists())
        
    def test_create_guidebook(self):
        """test creating the guidebook for a rental unit"""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with availability preferences")
        
        guidebook = models.Guidebook.objects.create(rental_unit=rental_unit)
        
        self.assertTrue(models.Guidebook.objects.filter(rental_unit=guidebook.rental_unit).exists())
        
    def test_create_place(self):
        """test creating a place"""
        user = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=user, title="a new home with availability preferences")

        place = models.Place.objects.create(rental_unit=rental_unit, name='El Shah de los Kebabs', category='Restaurant')
        
        self.assertTrue(models.Place.objects.filter(id=place.id).exists())
        
    def test_create_reservation_request(self):
        """test creating a reservation"""
        host = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=host, title="a new home for rent")
        guest = create_user(email='guest@example.com', password='password123')
        
        reservation_request = models.ReservationRequest.objects.create(
            rental_unit=rental_unit, 
            user=guest,
            check_in=date(2023,6,20),
            check_out=date(2023,6,28)
        )
        
        self.assertTrue(models.ReservationRequest.objects.filter(id=reservation_request.id).exists())
        
    def test_create_reservation(self):
        """test creating a reservation"""
        host = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=host, title="a new home for rent")
        guest = create_user(email='guest@example.com', password='password123')
        
        reservation = models.Reservation.objects.create(
            rental_unit=rental_unit, 
            user=guest,
            check_in=date(2023,6,20),
            check_out=date(2023,6,28)
        )
        
        self.assertTrue(models.Reservation.objects.filter(id=reservation.id).exists())
        
    def test_create_cancellation_request(self):
        """test creating a reservation cancellation request"""
        host = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=host, title="a new home for rent")
        guest = create_user(email='guest@example.com', password='password123')
        
        reservation = models.Reservation.objects.create(
            rental_unit=rental_unit, 
            user=guest,
            check_in=now + timedelta(days=14),
            check_out=now + timedelta(days=21)
        )
        
        cancellation_request = models.CancellationRequest.objects.create(
            user=guest,
            reservation=reservation,
        )
        
        self.assertTrue(models.CancellationRequest.objects.filter(id=cancellation_request.id).exists())
        
    def test_create_change_request(self):
        """test creating a reservation cancellation request"""
        host = create_superuser(email='test@example.com', password='test1234')
        rental_unit = models.RentalUnit.objects.create(user=host, title="a new home for rent")
        guest = create_user(email='guest@example.com', password='password123')
        
        reservation = models.Reservation.objects.create(
            rental_unit=rental_unit, 
            user=guest,
            check_in=now + timedelta(days=14),
            check_out=now + timedelta(days=21)
        )
        
        change_request = models.ChangeRequest.objects.create(
            user=guest,
            reservation=reservation,
            new_check_in=now + timedelta(days=15),
            new_check_out=now + timedelta(days=22)
        )
        
        self.assertTrue(models.ChangeRequest.objects.filter(id=change_request.id).exists())
        
        