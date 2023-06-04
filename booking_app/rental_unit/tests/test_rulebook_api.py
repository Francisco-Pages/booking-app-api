"""
tests for rulebook API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, Rulebook

from rental_unit.serializers import (
    RulebookSerializer,
    RulebookDetailSerializer
)


RULEBOOK_URL = reverse('rental_unit:rulebook-list')

## HELPER FUNCTIONS
def detail_url(rulebook_id):
    """create and return a detailed rulebook URL"""
    return reverse('rental_unit:rulebook-detail', args=[rulebook_id])

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

# def create_rulebook(rental_unit_id, **params):
#     """create and return a rulebook for a rental unit"""
#     defaults = {
#         'min_stay': 1,
#         'max_stay': 7,
#         'min_notice': 1,
#         'max_notice': 365,
#         'prep_time': 72,
#         'instant_booking': False
#     }
#     defaults.update(params)
    
#     rulebook = Rulebook.objects.create(rental_unit=rental_unit_id, **defaults)
    
#     return rulebook

def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_superuser(**params):
    """create and return a new user"""
    return get_user_model().objects.create_superuser(**params)


### TEST HANDLERS ###
class PublicRulebookApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_get_rulebook_by_non_auth(self):
        """test that unauthenticated requests can read rulebooks"""
        result = self.client.get(RULEBOOK_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_rulebook_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed rulebook"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        rulebook = Rulebook.objects.create(rental_unit=rental_unit)
        
        url = detail_url(rulebook.rental_unit.id)
        result = self.client.get(url)
        serializer = RulebookDetailSerializer(rulebook)

        self.assertEqual(result.data, serializer.data)
        
        
class PrivateRulebookApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_all_rulebooks_list(self):
        """test retrieving a list of Rulebooks"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        Rulebook.objects.create(rental_unit=rental_unit)
        Rulebook.objects.create(rental_unit=rental_unit_two)
        
        result = self.client.get(RULEBOOK_URL)
        
        rulebooks = Rulebook.objects.all().order_by('-rental_unit')
        serializer = RulebookSerializer(rulebooks, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_rulebook_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)
        rulebook = Rulebook.objects.create(rental_unit=rental_unit)
        
        url = detail_url(rulebook.rental_unit.id)
        result = self.client.get(url)

        serializer = RulebookDetailSerializer(rulebook)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_create_rulebook(self):
        """test error when creating a rulebook by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(RULEBOOK_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Rulebook.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    # def test_error_partial_update(self):
    #     """test error patch of a rulebook by a non administrator"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     original_min_stay = 1
    #     original_min_notice = 1
        
    #     rulebook = Rulebook.objects.create(
    #         rental_unit=rental_unit, 
    #         min_stay=original_min_stay,
    #         min_notice=original_min_notice
    #     )

    #     payload = {
    #         'rental_unit':rental_unit.id,
    #         'min_stay': 2
    #     }
        
    #     url = detail_url(rulebook.rental_unit.id)
    #     result = self.client.patch(url, payload)

    #     self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
    #     rulebook.refresh_from_db()
    #     self.assertEqual(rulebook.min_notice, original_min_notice)
    #     self.assertEqual(rulebook.min_stay, original_min_stay)
        
        
    # def test_error_full_update(self):
    #     """test error of put of rulebook"""
    #     rental_unit = create_rental_unit(user=self.user)
        
    #     original_values = {
    #         'min_stay': 7,
    #         'max_stay': 8,
    #         'min_notice': 30,
    #         'max_notice': 31,
    #         'prep_time': 48,
    #         'instant_booking': False
    #     }
        
    #     rulebook = create_rulebook(rental_unit_id=rental_unit, **original_values)
        
    #     payload = {
    #         'rental_unit': rulebook.rental_unit.id,
    #         'min_stay': 7,
    #         'max_stay': 8,
    #         'min_notice': 30,
    #         'max_notice': 31,
    #         'prep_time': 48,
    #         'instant_booking': True
    #     }
    #     url = detail_url(rulebook.rental_unit.id)
        
    #     result = self.client.put(url, payload)

    #     self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
    #     rulebook.refresh_from_db()
    #     flag = 0
    #     for k, v in original_values.items():
    #         flag += 1
    #         if flag == 1:
    #             continue
    #         self.assertEqual(getattr(rulebook, k), v)

    def test_error_delete_rulebook(self):
        """test error deleting a rulebook by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        rulebook = Rulebook.objects.create(rental_unit=rental_unit)
        
        url = detail_url(rulebook.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Rulebook.objects.filter(rental_unit=rulebook.rental_unit.id).exists())
        
class AdminRulebookApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_rulebook(self):
        """test creating a rulebook by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(RULEBOOK_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Rulebook.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    # def test_partial_update(self):
    #     """test patch of a rulebook by an administrator"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     original_min_stay = 1
    #     original_min_notice = 1
        
    #     rulebook = Rulebook.objects.create(
    #         rental_unit=rental_unit, 
    #         min_stay=original_min_stay,
    #         min_notice=original_min_notice
    #     )

    #     payload = {
    #         'rental_unit': rulebook.rental_unit.id,
    #         'min_stay': 2
    #     }
        
    #     url = detail_url(rulebook.rental_unit.id)
    #     result = self.client.patch(url, payload)
        
    #     self.assertEqual(result.status_code, status.HTTP_200_OK)
    #     rulebook.refresh_from_db()
    #     self.assertEqual(rulebook.min_notice, original_min_notice)
    #     self.assertEqual(rulebook.min_stay, payload['min_stay'])
        
    # def test_full_update(self):
    #     """test put of rulebook"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     rulebook = Rulebook.objects.create(rental_unit=rental_unit)
        
    #     payload = {
    #         'rental_unit': rulebook.rental_unit.id,
    #         'min_stay': 7,
    #         'max_stay': 8,
    #         'min_notice': 30,
    #         'max_notice': 31,
    #         'prep_time': 48,
    #         'instant_booking': False
    #     }
    #     url = detail_url(rulebook.rental_unit.id)
        
    #     result = self.client.put(url, payload)

    #     self.assertEqual(result.status_code, status.HTTP_200_OK)
    #     rulebook.refresh_from_db()
    #     flag = 0
    #     for k, v in payload.items():
    #         flag += 1
    #         if flag == 1:
    #             continue
    #         self.assertEqual(getattr(rulebook, k), v)
        
    def test_delete_rulebook(self):
        """test deleting a rulebook is successful"""
        rental_unit = create_rental_unit(user=self.user)
        rulebook = Rulebook.objects.create(rental_unit=rental_unit)
        
        url = detail_url(rulebook.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Rulebook.objects.filter(rental_unit=rulebook.rental_unit.id).exists())