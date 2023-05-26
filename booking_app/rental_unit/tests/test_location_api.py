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
    LocationSerializer
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

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateLocationApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.user = create_user(email='test@example.com', password='test1234')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_retrieve_amenities(self):
        """test retrieving a list of Location"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        Location.objects.create(rental_unit=rental_unit)
        Location.objects.create(rental_unit=rental_unit_two)
        
        result = self.client.get(LOCATION_URL)
        
        locations = Location.objects.all().order_by('-rental_unit')
        serializer = LocationSerializer(locations, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
