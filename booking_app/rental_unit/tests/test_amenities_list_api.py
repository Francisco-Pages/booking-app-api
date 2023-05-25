"""
tests for amenities list API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import AmenitiesList, RentalUnit

from rental_unit.serializers import (
    AmenitiesListSerializer
)


AMENITIES_LIST_URL = reverse('rental_unit:amenitieslist-list')


## HELPER FUNCTIONS
def detail_url(rental_unit_id):
    """create and return a detailed rental unit URL"""
    return reverse('rental_unit:rentalunit-detail', args=[rental_unit_id])

def create_rental_unit(user, **params):
    """create and return a rental unit object"""
    defaults = {
        'title':'Title of property',
        'description':'A unique description of your home',
        'unit_type':'apartment',
        'status':'inactive',
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
class PublicAmenitiesListApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(AMENITIES_LIST_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class PrivateAmenitiesListApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.user = create_user(email='test@example.com', password='test1234')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_retrieve_amenities(self):
        """test retrieving a list of amenities lists"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        AmenitiesList.objects.create(rental_unit=rental_unit)
        AmenitiesList.objects.create(rental_unit=rental_unit_two)
        
        result = self.client.get(AMENITIES_LIST_URL)
        
        amenities = AmenitiesList.objects.all().order_by('-rental_unit')
        serializer = AmenitiesListSerializer(amenities, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)