"""
tests for availability API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, Availability

from rental_unit.serializers import (
    AvailabilitySerializer,
    AvailabilityDetailSerializer
)


AVAILABILITY_URL = reverse('rental_unit:availability-list')

## HELPER FUNCTIONS
def detail_url(availability_id):
    """create and return a detailed availability URL"""
    return reverse('rental_unit:availability-detail', args=[availability_id])

def create_rental_unit(user, **params):
    """create and return a rental unit object"""
    defaults = {
        'title':'Title of property',
        'description':'A unique description of your home',
        'unit_type':'Apartment',
        'status':'Inactive',
        'max_guests':1,
    }
    defaults.update(params)

    rental_unit = RentalUnit.objects.create(user=user, **defaults)
    return rental_unit

def create_availability(rental_unit_id, **params):
    """create and return a availability for a rental unit"""
    defaults = {
        'min_stay': 1,
        'max_stay': 7,
        'min_notice': 1,
        'max_notice': 365,
        'prep_time': 72,
        'instant_booking': False
    }
    defaults.update(params)
    
    availability = Availability.objects.create(rental_unit=rental_unit_id, **defaults)
    
    return availability

def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_superuser(**params):
    """create and return a new user"""
    return get_user_model().objects.create_superuser(**params)


### TEST HANDLERS ###
class PublicAvailabilityApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_get_availability_by_non_auth(self):
        """test that unauthenticated requests can read availabilitys"""
        result = self.client.get(AVAILABILITY_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_availability_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed availability"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        url = detail_url(availability.rental_unit.id)
        result = self.client.get(url)
        serializer = AvailabilityDetailSerializer(availability)

        self.assertEqual(result.data, serializer.data)
        
        
class PrivateAvailabilityApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_all_availabilitys_list(self):
        """test retrieving a list of Availabilitys"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        Availability.objects.create(rental_unit=rental_unit)
        Availability.objects.create(rental_unit=rental_unit_two)
        
        result = self.client.get(AVAILABILITY_URL)
        
        availabilitys = Availability.objects.all().order_by('-rental_unit')
        serializer = AvailabilitySerializer(availabilitys, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_availability_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        url = detail_url(availability.rental_unit.id)
        result = self.client.get(url)

        serializer = AvailabilityDetailSerializer(availability)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_create_availability(self):
        """test error when creating a availability by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(AVAILABILITY_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Availability.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_error_partial_update(self):
        """test error patch of a availability by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_min_stay = 1
        original_min_notice = 1
        
        availability = Availability.objects.create(
            rental_unit=rental_unit, 
            min_stay=original_min_stay,
            min_notice=original_min_notice
        )

        payload = {
            'rental_unit':rental_unit.id,
            'min_stay': 2
        }
        
        url = detail_url(availability.rental_unit.id)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        availability.refresh_from_db()
        self.assertEqual(availability.min_notice, original_min_notice)
        self.assertEqual(availability.min_stay, original_min_stay)
        
        
    def test_error_full_update(self):
        """test error of put of availability"""
        rental_unit = create_rental_unit(user=self.user)
        
        original_values = {
            'min_stay': 7,
            'max_stay': 8,
            'min_notice': 30,
            'max_notice': 31,
            'prep_time': 48,
            'instant_booking': False
        }
        
        availability = create_availability(rental_unit_id=rental_unit, **original_values)
        
        payload = {
            'rental_unit': availability.rental_unit.id,
            'min_stay': 7,
            'max_stay': 8,
            'min_notice': 30,
            'max_notice': 31,
            'prep_time': 48,
            'instant_booking': True
        }
        url = detail_url(availability.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        availability.refresh_from_db()
        flag = 0
        for k, v in original_values.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(availability, k), v)

    def test_error_delete_availability(self):
        """test error deleting a availability by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        url = detail_url(availability.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Availability.objects.filter(rental_unit=availability.rental_unit.id).exists())
        
class AdminAvailabilityApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_availability(self):
        """test creating a availability by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(AVAILABILITY_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Availability.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_partial_update(self):
        """test patch of a availability by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_min_stay = 1
        original_min_notice = 1
        
        availability = Availability.objects.create(
            rental_unit=rental_unit, 
            min_stay=original_min_stay,
            min_notice=original_min_notice
        )

        payload = {
            'rental_unit': availability.rental_unit.id,
            'min_stay': 2
        }
        
        url = detail_url(availability.rental_unit.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        availability.refresh_from_db()
        self.assertEqual(availability.min_notice, original_min_notice)
        self.assertEqual(availability.min_stay, payload['min_stay'])
        
    def test_full_update(self):
        """test put of availability"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': availability.rental_unit.id,
            'min_stay': 7,
            'max_stay': 8,
            'min_notice': 30,
            'max_notice': 31,
            'prep_time': 48,
            'instant_booking': False
        }
        url = detail_url(availability.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        availability.refresh_from_db()
        flag = 0
        for k, v in payload.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(availability, k), v)
        
    def test_delete_availability(self):
        """test deleting a availability is successful"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        url = detail_url(availability.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Availability.objects.filter(rental_unit=availability.rental_unit.id).exists())