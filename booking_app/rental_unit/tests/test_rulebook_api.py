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
        'status':False,
        'max_guests':1,
    }
    defaults.update(params)

    rental_unit = RentalUnit.objects.create(user=user, **defaults)
    return rental_unit

def create_rulebook(rental_unit_id, **params):
    """create and return a rulebook for a rental unit"""
    defaults = {
        'cancellation_policy': 'Flexible',
        'house_rules': 'No rules',
        'pets_allowed': False,
        'events_allowed': False,
        'smoking_allowed': False,
        'commercial_photo_film_allowed': False,
        'guest_requirements': 'No requirements',
        'laws_and_regulations': 'No laws'
    }
    defaults.update(params)
    
    rulebook = Rulebook.objects.create(rental_unit=rental_unit_id, **defaults)
    
    return rulebook

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
        
    def test_error_partial_update(self):
        """test error patch of a rulebook by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_cancellation_policy = 'Flexible'
        original_pets_allowed = True
        
        rulebook = Rulebook.objects.create(
            rental_unit=rental_unit, 
            cancellation_policy=original_cancellation_policy,
            pets_allowed=original_pets_allowed
        )

        payload = {
            'rental_unit': rulebook.rental_unit.id,
            'pets_allowed': False
        }
        
        url = detail_url(rulebook.rental_unit.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        rulebook.refresh_from_db()
        self.assertEqual(rulebook.cancellation_policy, original_cancellation_policy)
        self.assertEqual(rulebook.pets_allowed, original_pets_allowed)
        
        
    def test_error_full_update(self):
        """test error of put of rulebook"""
        rental_unit = create_rental_unit(user=self.user)
        
        original_values = {
            'cancellation_policy': 'Flexible',
            'house_rules': 'No rules',
            'pets_allowed': False,
            'events_allowed': False,
            'smoking_allowed': False,
            'commercial_photo_film_allowed': False,
            'guest_requirements': 'No requirements',
            'laws_and_regulations': 'No laws'
        }
        
        rulebook = create_rulebook(rental_unit_id=rental_unit, **original_values)
        
        payload = {
            'rental_unit': rulebook.rental_unit.id,
            'cancellation_policy': 'Firm',
            'house_rules': 'sample house rules, no jumping on the beds',
            'pets_allowed': True,
            'events_allowed': True,
            'smoking_allowed': True,
            'commercial_photo_film_allowed': True,
            'guest_requirements': 'must be over 18 years old to book',
            'laws_and_regulations': 'guns are not permitted'
        }
        url = detail_url(rulebook.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        rulebook.refresh_from_db()
        flag = 0
        for k, v in original_values.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(rulebook, k), v)

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
        
    def test_partial_update(self):
        """test patch of a rulebook by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_cancellation_policy = 'Flexible'
        original_pets_allowed = True
        
        rulebook = Rulebook.objects.create(
            rental_unit=rental_unit, 
            cancellation_policy=original_cancellation_policy,
            pets_allowed=original_pets_allowed
        )

        payload = {
            'rental_unit': rulebook.rental_unit.id,
            'pets_allowed': False
        }
        
        url = detail_url(rulebook.rental_unit.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        rulebook.refresh_from_db()
        self.assertEqual(rulebook.cancellation_policy, original_cancellation_policy)
        self.assertEqual(rulebook.pets_allowed, payload['pets_allowed'])
        
    def test_full_update(self):
        """test put of rulebook"""
        rental_unit = create_rental_unit(user=self.user)
        rulebook = Rulebook.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': rulebook.rental_unit.id,
            'cancellation_policy': 'Firm',
            'house_rules': 'sample house rules, no jumping on the beds',
            'pets_allowed': True,
            'events_allowed': True,
            'smoking_allowed': True,
            'commercial_photo_film_allowed': True,
            'guest_requirements': 'must be over 18 years old to book',
            'laws_and_regulations': 'guns are not permitted'
        }
        url = detail_url(rulebook.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        rulebook.refresh_from_db()
        flag = 0
        for k, v in payload.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(rulebook, k), v)
        
    def test_delete_rulebook(self):
        """test deleting a rulebook is successful"""
        rental_unit = create_rental_unit(user=self.user)
        rulebook = Rulebook.objects.create(rental_unit=rental_unit)
        
        url = detail_url(rulebook.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Rulebook.objects.filter(rental_unit=rulebook.rental_unit.id).exists())