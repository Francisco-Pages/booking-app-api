"""
tests for location API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import AmenitiesList, RentalUnit, Location

from rental_unit.serializers import (
    LocationSerializer,
    LocationDetailSerializer
)


LOCATION_URL = reverse('rental_unit:location-list')

## HELPER FUNCTIONS
def detail_url(location_id):
    """create and return a detailed amenities list URL"""
    return reverse('rental_unit:location-detail', args=[location_id])

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

def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_superuser(**params):
    """create and return a new user"""
    return get_user_model().objects.create_superuser(**params)


### TEST HANDLERS ###
class PublicLocationApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(LOCATION_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
class PrivateLocationApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_retrieve_locations_list(self):
        """test retrieving a list of Locations"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        Location.objects.create(rental_unit=rental_unit)
        Location.objects.create(rental_unit=rental_unit_two)
        
        result = self.client.get(LOCATION_URL)
        
        locations = Location.objects.all().order_by('-rental_unit')
        serializer = LocationSerializer(locations, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_location_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)
        location = Location.objects.create(rental_unit=rental_unit)
        
        url = detail_url(location.rental_unit.id)
        result = self.client.get(url)

        serializer = LocationDetailSerializer(location)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_create_location(self):
        """test error when creating a location by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(LOCATION_URL, payload)

        self.assertFalse(Location.objects.filter(rental_unit=payload['rental_unit']).exists())
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class AdminLocationApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_location(self):
        """test creating a location by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(LOCATION_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Location.objects.filter(rental_unit=payload['rental_unit']).exists())