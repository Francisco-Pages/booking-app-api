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
def detail_url(amenities_list_id):
    """create and return a detailed amenities list URL"""
    return reverse('rental_unit:amenitieslist-detail', args=[amenities_list_id])

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
        
    # def test_error_create_amenities_list(self):
    #     """test error creating a rental unit by a non administrator"""
    #     user = create_user(
    #         email='test1@example.com',
    #         password='testpass123'
    #         )
    #     rental_unit = create_rental_unit(user=user)       
        
    #     payload = {
    #         'rental_unit': rental_unit.id,
    #         'popular_essentials':True,
    #     }
    #     result = self.client.post(AMENITIES_LIST_URL, payload)

    #     self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertFalse(AmenitiesList.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    # def test_error_update_amenities_list(self):
    #     """Test error only administrators can update amenities lists"""
    #     rental_unit = create_rental_unit(user=self.user)    
    #     amenities_list = AmenitiesList.objects.create(
    #         rental_unit=rental_unit,
    #         popular_essentials=False
    #     )
        
    #     payload = {'popular_essentials':True}
    #     url = detail_url(amenities_list.rental_unit)
    #     result = self.client.patch(url, payload)
        
    #     self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
    #     amenities_list.refresh_from_db()
    #     self.assertFalse(amenities_list.popular_essentials)
        
    def test_error_delete_amenities_list(self):
        """test error only administrators can delete an amenities list"""
        rental_unit = create_rental_unit(user=self.user)    
        amenities_list = AmenitiesList.objects.create(rental_unit=rental_unit)
        
        url = detail_url(amenities_list.rental_unit)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        amenities = AmenitiesList.objects.filter(rental_unit=rental_unit)
        self.assertTrue(amenities.exists())
    
class AdminAmenitiesListApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)    
        
    # def test_create_amenities_list(self):
    #     """test creating a rental unit by an administrator"""
    #     super_user = create_superuser(
    #         email='testadmin2@example.com',
    #         password='testpass123'
    #         )
    #     rental_unit = create_rental_unit(user=super_user)    
        
    #     payload = {
    #         'rental_unit': rental_unit.id,
    #         'popular_essentials':True,
    #     }
    #     url = detail_url(payload['rental_unit'])
    #     result = self.client.post(url, payload)
        
    #     self.assertTrue(AmenitiesList.objects.filter(rental_unit=payload['rental_unit']).exists())
    #     self.assertEqual(result.status_code, status.HTTP_201_CREATED)
    
    # def test_update_amenities_list(self):
    #     rental_unit = create_rental_unit(user=self.user)    
    #     amenities_list = AmenitiesList.objects.create(rental_unit=rental_unit)
        
    #     payload = {'popular_essentials':True}
    #     url = detail_url(amenities_list.rental_unit)
    #     result = self.client.patch(url, payload)
        
    #     self.assertEqual(result.status_code, status.HTTP_200_OK)
    #     amenities_list.refresh_from_db()
    #     self.assertEqual(amenities_list.popular_essentials, payload['popular_essentials'])
        
    # def test_delete_amenities_list(self):
    #     """test deleting an amenities list"""
    #     rental_unit = create_rental_unit(user=self.user)    
    #     amenities_list = AmenitiesList.objects.create(rental_unit=rental_unit)
        
    #     url = detail_url(amenities_list.rental_unit)
    #     result = self.client.delete(url)
        
    #     self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
    #     amenities = AmenitiesList.objects.filter(rental_unit=rental_unit)
    #     self.assertFalse(amenities.exists())