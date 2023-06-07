"""
tests for amenities list API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, AmenitiesList

from rental_unit.serializers import (
    AmenitiesListSerializer,
    AmenitiesListDetailSerializer
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
        'status': False,
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

    def test_get_amenities_list_by_non_auth(self):
        """test that unauthenticated requests can read amenities"""
        result = self.client.get(AMENITIES_LIST_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_location_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed location"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        amenities_list = AmenitiesList.objects.create(rental_unit=rental_unit)
        
        url = detail_url(amenities_list.rental_unit.id)
        result = self.client.get(url)
        serializer = AmenitiesListDetailSerializer(amenities_list)

        self.assertEqual(result.data, serializer.data)
        
        
class PrivateAmenitiesListApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_all_amenities_list(self):
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
        
    def test_get_amenities_list_detail(self):
        """test get amenities list detail"""
        rental_unit = create_rental_unit(user=self.user)
        amenities_list = AmenitiesList.objects.create(rental_unit=rental_unit)
        
        url = detail_url(amenities_list.rental_unit.id)
        result = self.client.get(url)

        serializer = AmenitiesListDetailSerializer(amenities_list)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_create_amenities_list(self):
        """test error creating a rental unit by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)    
        
        payload = {
            'rental_unit': rental_unit.id
        }
        result = self.client.post(AMENITIES_LIST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(AmenitiesList.objects.filter(rental_unit=payload['rental_unit']).exists())

    def test_error_partial_update_amenities_list(self):
        """test error when patch of an amenities list for a rental unit by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)    
        original_pool = False
        original_pe = False
        original_be = False
        
        amenities_list = AmenitiesList.objects.create(
            rental_unit=rental_unit,
            popular_pool=original_pool,
            popular_essentials=original_pe,
            bedroom_essentials=original_be
        )
        
        payload = {
            'popular_essentials':True,
            'bedroom_essentials': True,
        }
        
        url = detail_url(amenities_list.rental_unit.id)
        result = self.client.patch(url, payload)
    
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        amenities_list.refresh_from_db()
        
        self.assertEqual(amenities_list.popular_essentials, original_pe)
        self.assertEqual(amenities_list.bedroom_essentials, original_be)
    
        
    def test_error_delete_amenities_list(self):
        """test error only administrators can delete an amenities list"""
        rental_unit = create_rental_unit(user=self.user)    
        amenities_list = AmenitiesList.objects.create(rental_unit=rental_unit)
        
        url = detail_url(amenities_list.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(AmenitiesList.objects.filter(rental_unit=rental_unit).exists())
    
class AdminAmenitiesListApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)    
        
    def test_create_amenities_list(self):
        """test creating an amenities list by an administrator"""
        rental_unit = create_rental_unit(user=self.user)    
        
        payload = {
            'rental_unit': rental_unit.id
        }
        result = self.client.post(AMENITIES_LIST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AmenitiesList.objects.filter(rental_unit=payload['rental_unit']).exists())
    
    def test_partial_update_amenities_list(self):
        """test patch of an amenities list for a rental unit"""
        rental_unit = create_rental_unit(user=self.user)    
        original_pool = False
        original_pe = False
        original_be = False
        
        amenities_list = AmenitiesList.objects.create(
            rental_unit=rental_unit,
            popular_pool=original_pool,
            popular_essentials=original_pe,
            bedroom_essentials=original_be
        )
        
        payload = {
            'rental_unit': amenities_list.rental_unit.id,
            'popular_essentials':True,
            'bedroom_essentials': True,
        }
        
        url = detail_url(amenities_list.rental_unit.id)
        result = self.client.patch(url, payload)
    
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        amenities_list.refresh_from_db()
        self.assertEqual(amenities_list.popular_pool, original_pool)
        self.assertEqual(amenities_list.popular_essentials, payload['popular_essentials'])
        self.assertEqual(amenities_list.bedroom_essentials, payload['bedroom_essentials'])
        
    # def test_full_update(self):
    #     """test put of an amenities list"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     amenities_list = AmenitiesList.objects.create(rental_unit=rental_unit)
        
    #     amenities_fields = vars(amenities_list)
    #     # del amenities_fields['_state']
    #     # del amenities_fields['_prefetched_objects_cache']
    #     # for key in amenities_fields.keys():
    #     #     amenities_fields[key] = True
            
    #     payload = {}    
    #     for k,v in amenities_fields.items():
    #         if amenities_fields[k] in getattr(amenities_list, k):
    #             payload[k] = v
            
    #     for k,v in payload.items():
    #         print(k,v)
        
    #     url = detail_url(amenities_list.rental_unit.id)
        
    #     result = self.client.put(url, payload)

    #     self.assertEqual(result.status_code, status.HTTP_200_OK)
    #     amenities_list.refresh_from_db()
    #     flag = 0
    #     for k, v in payload.items():
    #         flag += 1
    #         if flag == 1:
    #             continue
    #         self.assertEqual(getattr(amenities_list, k), v)
        
        
    def test_delete_amenities_list(self):
        """test deleting an amenities list"""
        rental_unit = create_rental_unit(user=self.user)    
        amenities_list = AmenitiesList.objects.create(rental_unit=rental_unit)
        
        url = detail_url(amenities_list.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AmenitiesList.objects.filter(rental_unit=amenities_list.rental_unit.id).exists())