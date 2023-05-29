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

def create_location(rental_unit_id, **params):
    """create and return a location for a rental unit"""
    defaults = {
            'neighborhood_description': 'default description',
            'getting_around': 'default getting around',
            'location_sharing': False,
            'address1': 'default address 1',
            'address2': 'default address 2',
            'zip_code': '123456',
            'city': 'default city',
            'country': 'USA',
            'longitude': Decimal('1.11111'),
            'latitude': Decimal('1.11111'),
        }
    defaults.update(params)
    
    location = Location.objects.create(rental_unit=rental_unit_id, **defaults)
    
    return location

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

    def test_get_location_by_non_auth(self):
        """test that unauthenticated requests can read locations"""
        result = self.client.get(LOCATION_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_location_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed location"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        location = create_location(rental_unit_id=rental_unit)
        
        url = detail_url(location.rental_unit.id)
        result = self.client.get(url)
        serializer = LocationDetailSerializer(location)

        self.assertEqual(result.data, serializer.data)
        
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

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Location.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_error_partial_update(self):
        """test error patch of a location by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_address1 = '2519 golf view dr'
        original_city = 'weston'
        
        location = Location.objects.create(
            rental_unit=rental_unit, 
            address1=original_address1,
            city=original_city
        )

        payload = {
            'rental_unit':rental_unit.id,
            'address1': 'a new address'
        }
        
        url = detail_url(location.rental_unit.id)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        location.refresh_from_db()
        self.assertEqual(location.city, original_city)
        self.assertEqual(location.address1, original_address1)
        
    def test_error_full_update(self):
        """test error of put of location"""
        rental_unit = create_rental_unit(user=self.user)
        
        original_values = {
            'neighborhood_description': 'default description',
            'getting_around': 'default getting around',
            'location_sharing': False,
            'address1': 'default address 1',
            'address2': 'default address 2',
            'zip_code': '123456',
            'city': 'default city',
            'country': 'USA',
            'longitude': Decimal('1.11111'),
            'latitude': Decimal('1.11111'),
        }
        location = create_location(rental_unit_id=rental_unit, **original_values)
        
        payload = {
            'rental_unit': location.rental_unit.id,
            'neighborhood_description': 'lots of constructions, lots of mosquitos.',
            'getting_around': 'do not move the furniture, thank you.',
            'location_sharing': False,
            'address1': '2201 sole mia sq ln',
            'address2': 'apt 232',
            'zip_code': '33160',
            'city': 'North Miami',
            'country': 'USA',
            'longitude': Decimal('4.69584'),
            'latitude': Decimal('3.1212'),
        }
        
        url = detail_url(location.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        location.refresh_from_db()
        flag = 0
        for k, v in original_values.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(location, k), v)

    def test_error_delete_location(self):
        """test error deleting a location by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        location = create_location(rental_unit_id=rental_unit)
        
        url = detail_url(location.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Location.objects.filter(rental_unit=location.rental_unit.id).exists())
        
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
        
    def test_partial_update(self):
        """test patch of a location by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_address1 = '2519 golf view dr'
        original_city = 'weston'
        
        location = Location.objects.create(
            rental_unit=rental_unit, 
            address1=original_address1,
            city=original_city
        )

        payload = {
            'rental_unit': location.rental_unit.id,
            'address1': 'a new address'
        }
        
        url = detail_url(location.rental_unit.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        location.refresh_from_db()
        self.assertEqual(location.city, original_city)
        self.assertEqual(location.address1, payload['address1'])
        
    def test_full_update(self):
        """test put of location"""
        rental_unit = create_rental_unit(user=self.user)
        location = Location.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': location.rental_unit.id,
            'neighborhood_description': 'lots of constructions, lots of mosquitos.',
            'getting_around': 'do not move the furniture, thank you.',
            'location_sharing': False,
            'address1': '2201 sole mia sq ln',
            'address2': 'apt 232',
            'zip_code': '33160',
            'city': 'North Miami',
            'country': 'USA',
            'longitude': Decimal('4.69584'),
            'latitude': Decimal('3.1212'),
        }
        url = detail_url(location.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        location.refresh_from_db()
        flag = 0
        for k, v in payload.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(location, k), v)
        
    def test_delete_location(self):
        """test deleting a location is successful"""
        rental_unit = create_rental_unit(user=self.user)
        location = create_location(rental_unit_id=rental_unit)
        
        url = detail_url(location.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Location.objects.filter(rental_unit=location.rental_unit.id).exists())