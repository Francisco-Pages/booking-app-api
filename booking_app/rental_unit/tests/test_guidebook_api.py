"""
tests for guidebook API
"""
from decimal import Decimal
from datetime import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, Guidebook, Place

from rental_unit.serializers import (
    GuidebookSerializer,
    GuidebookDetailSerializer
)


GUIDEBOOK_URL = reverse('rental_unit:guidebook-list')

## HELPER FUNCTIONS
def detail_url(guidebook_id):
    """create and return a detailed amenities list URL"""
    return reverse('rental_unit:guidebook-detail', args=[guidebook_id])

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

def create_guidebook(rental_unit_id, **params):
    """create and return a guidebook for a rental unit"""
    defaults = {
        'check_in_start_time': time(10, 0),
        'check_in_end_time': time(17, 0),
        'check_out_time': time(8, 0),
        'check_in_method': 'keyless',
        'check_in_instructions': 'follow the path',
        # 'places_of_interest': '123456',
        'house_manual': 'wifi name is ... and pasword is ...',
    }
    defaults.update(params)
    
    guidebook = Guidebook.objects.create(rental_unit=rental_unit_id, **defaults)
    
    return guidebook

def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_superuser(**params):
    """create and return a new user"""
    return get_user_model().objects.create_superuser(**params)


### TEST HANDLERS ###
class PublicGuidebookApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_get_guidebook_by_non_auth(self):
        """test that unauthenticated requests can read guidebooks"""
        result = self.client.get(GUIDEBOOK_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_guidebook_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed guidebook"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        guidebook = create_guidebook(rental_unit_id=rental_unit)
        
        url = detail_url(guidebook.rental_unit.id)
        result = self.client.get(url)
        serializer = GuidebookDetailSerializer(guidebook)

        self.assertEqual(result.data, serializer.data)
        
class PrivateGuidebookApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_all_guidebooks_list(self):
        """test retrieving a list of Guidebooks"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        Guidebook.objects.create(rental_unit=rental_unit)
        Guidebook.objects.create(rental_unit=rental_unit_two)
        
        result = self.client.get(GUIDEBOOK_URL)
        
        guidebooks = Guidebook.objects.all().order_by('-rental_unit')
        serializer = GuidebookSerializer(guidebooks, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_guidebook_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)
        guidebook = Guidebook.objects.create(rental_unit=rental_unit)
        
        url = detail_url(guidebook.rental_unit.id)
        result = self.client.get(url)

        serializer = GuidebookDetailSerializer(guidebook)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_create_guidebook(self):
        """test error when creating a guidebook by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(GUIDEBOOK_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Guidebook.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_error_partial_update(self):
        """test error patch of a guidebook by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_check_in_start_time = time(12,30)
        original_check_out_time = time(10,0)
        
        guidebook = Guidebook.objects.create(
            rental_unit=rental_unit, 
            check_in_start_time=original_check_in_start_time,
            check_out_time=original_check_out_time
        )

        payload = {
            'rental_unit':rental_unit.id,
            'check_out_time': time(9,0)
        }
        
        url = detail_url(guidebook.rental_unit.id)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        guidebook.refresh_from_db()
        self.assertEqual(guidebook.check_in_start_time, original_check_in_start_time)
        self.assertEqual(guidebook.check_out_time, original_check_out_time)
        
    def test_error_full_update(self):
        """test error of put of guidebook"""
        rental_unit = create_rental_unit(user=self.user)
        
        original_values = {
            'check_in_start_time': time(10, 0),
            'check_in_end_time': time(16, 0),
            'check_out_time': time(8, 0),
            'check_in_method': 'not in person',
            'check_in_instructions': 'follow the path and cross the pool over the alligator\'s mouth',
            'check_out_instructions': 'please leave keys at the kitchen top',
            'house_manual': 'wifi name is wifi123 and pasword is password123',
        }
        guidebook = create_guidebook(rental_unit_id=rental_unit, **original_values)
        
        payload = {
            'check_in_start_time': time(12, 0),
            'check_in_end_time': time(18, 0),
            'check_out_time': time(10, 0),
            'check_in_method': 'in person',
            'check_in_instructions': 'follow the path and cross the pool',
            'check_out_instructions': 'please leave keys inside the crocodile\'s mouth',
            'house_manual': 'wifi name is wifi and pasword is password',
        }
        
        url = detail_url(guidebook.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        guidebook.refresh_from_db()
        flag = 0
        for k, v in original_values.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(guidebook, k), v)

    def test_error_delete_guidebook(self):
        """test error deleting a guidebook by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        guidebook = create_guidebook(rental_unit_id=rental_unit)
        
        url = detail_url(guidebook.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Guidebook.objects.filter(rental_unit=guidebook.rental_unit.id).exists())
        
class AdminGuidebookApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_guidebook(self):
        """test creating a guidebook by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(GUIDEBOOK_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Guidebook.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_partial_update(self):
        """test patch of a guidebook by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_check_in_start_time = time(12,30)
        original_check_out_time = time(10,0)
        
        guidebook = Guidebook.objects.create(
            rental_unit=rental_unit, 
            check_in_start_time=original_check_in_start_time,
            check_out_time=original_check_out_time
        )

        payload = {
            'rental_unit':rental_unit.id,
            'check_out_time': time(9,0)
        }
        
        url = detail_url(guidebook.rental_unit.id)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        guidebook.refresh_from_db()
        self.assertEqual(guidebook.check_in_start_time, original_check_in_start_time)
        self.assertEqual(guidebook.check_out_time, payload['check_out_time'])
        
    def test_full_update(self):
        """test put of guidebook"""
        rental_unit = create_rental_unit(user=self.user)
        guidebook = Guidebook.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': rental_unit.id,
            'check_in_start_time': time(12, 0),
            'check_in_end_time': time(18, 0),
            'check_out_time': time(10, 0),
            'check_in_method': 'Lockbox',
            'check_in_instructions': 'follow the path and cross the pool',
            'check_out_instructions': 'leave the keys on the kitchen counter',
            'house_manual': 'wifi name is wifi and pasword is password',
        }
        url = detail_url(guidebook.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        guidebook.refresh_from_db()
        flag = 0
        for k, v in payload.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(guidebook, k), v)
        
    def test_delete_guidebook(self):
        """test deleting a guidebook is successful"""
        rental_unit = create_rental_unit(user=self.user)
        guidebook = create_guidebook(rental_unit_id=rental_unit)
        
        url = detail_url(guidebook.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Guidebook.objects.filter(rental_unit=guidebook.rental_unit.id).exists())
   