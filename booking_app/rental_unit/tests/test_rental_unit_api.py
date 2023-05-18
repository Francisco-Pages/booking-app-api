"""
tests for rental unit API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit

from rental_unit.serializers import (
    RentalUnitSerializer,
    RentalUnitDetailSerializer
)


RENTAL_UNIT_URL = reverse('rental_unit:rentalunit-list')


## HELPER FUNCTIONS
def detail_url(rental_unit_id):
    """create and return a detailed rental unit URL"""
    return reverse('rental_unit:rentalunit-detail', args=[rental_unit_id])

def create_rental_unit(user, **params):
    """create and return a rental unit object"""
    defaults = {
        'title':'Title of property',
        'price':100,
        'description':'A unique description of your home',
        'unit_type':'apartment',
        'status':'inactive',
        'max_guests':1,
        'wifi_name':'wifi name',
        'wifi_password':'wifi password ',
        'house_rules':'please make your bed before check out, thank you',
    }
    defaults.update(params)
    
    rental_unit = RentalUnit.objects.create(user=user, **defaults)
    
    return rental_unit

def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)

##TEST HANDLERS
class PublicRentalUnitApiTests(TestCase):
    """tests for unauthenticated API requests"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_auth_required(self):
        result = self.client.get(RENTAL_UNIT_URL)
        
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateRentalUnitApiTests(TestCase):
    """test authenticated API tests."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_rental_unit(self):
        create_rental_unit(user=self.user)
        create_rental_unit(user=self.user)
        
        result = self.client.get(RENTAL_UNIT_URL)
        
        rental_units = RentalUnit.objects.all().order_by('-id')
        serializer = RentalUnitSerializer(rental_units, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_rental_unit_list_limited_to_user(self):
        """test that the list of rental units is limited to user"""
        other_user = create_user(
            email='other@example.com',
            password='testpass123'
        )
        create_rental_unit(user=other_user)
        create_rental_unit(user=self.user)
        
        result = self.client.get(RENTAL_UNIT_URL)
        
        rental_units = RentalUnit.objects.filter(user=self.user)
        serializer = RentalUnitSerializer(rental_units, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_rental_unit_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)
        
        url = detail_url(rental_unit.id)
        result = self.client.get(url)
        
        serializer = RentalUnitDetailSerializer(rental_unit)
        self.assertEqual(result.data, serializer.data)        
        
    def test_create_rental_unit(self):
        """test creating a rental unit"""
        payload = {
            'title':'Title of property',
            'price':100,
        }
        result = self.client.post(RENTAL_UNIT_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        rental_unit = RentalUnit.objects.get(id=result.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(rental_unit, k), v)
        self.assertEqual(rental_unit.user, self.user)
        
    def test_partial_update(self):
        """test patch of a rental unit"""
        original_link = 'https://example.com/renta-unit.pdf'
        rental_unit = create_rental_unit(
            user=self.user,
            title='sample unit title',
            link=original_link,
        )
        
        payload = {'title': 'new unit title'}
        url = detail_url(rental_unit.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        rental_unit.refresh_from_db()
        self.assertEqual(rental_unit.title, payload['title'])
        self.assertEqual(rental_unit.link, original_link)
        self.assertEqual(rental_unit.user, self.user)
        
    def test_full_update(self):
        """test put of rental unit"""
        rental_unit = create_rental_unit(
            user=self.user,
            title='sample unit title',
            price=Decimal('100'),
            description='sample unit description',
        )
        
        payload = {
            'title': 'NEW Title of property',
            'price': Decimal('100.29'),
            'description': 'NEW A unique description of your home',
            'unit_type': 'Hotel',
            'status': 'Active',
            'max_guests': 1,
            'wifi_name': 'NEW wifi name',
            'wifi_password': 'NEW wifi password',
            'house_rules': 'NEW please make your bed before check out, thank you',
        }
        url = detail_url(rental_unit.id)
        result = self.client.put(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        rental_unit.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(rental_unit, k), v)
        self.assertEqual(rental_unit.user, self.user)
        
    def test_update_user_returns_error(self):
        """test changing the rental unit user returns an error"""
        new_user = create_user(
            email='testuser2@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {'user': new_user.id}
        url = detail_url(rental_unit.id)
        self.client.patch(url, payload)
        
        rental_unit.refresh_from_db()
        self.assertEqual(rental_unit.user, self.user)
        
    def test_delete_rental_unit(self):
        """test deleting a rental unit"""
        rental_unit = create_rental_unit(user=self.user)
        
        url = detail_url(rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RentalUnit.objects.filter(id=rental_unit.id).exists())
        
    def test_delete_other_users_rental_unit(self):
        """test deleting other user's rental units returns error"""
        new_user = create_user(
            email='testuser3@example.com',
            password='testpass123'
        )       
        rental_unit = create_rental_unit(user=new_user)
        
        url = detail_url(rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(RentalUnit.objects.filter(id=rental_unit.id).exists())
        