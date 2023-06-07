"""
tests for fee API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, Fee

from rental_unit.serializers import (
    FeeSerializer,
    FeeDetailSerializer
)


FEE_URL = reverse('rental_unit:fee-list')

def detail_url(fee_id):
    """create and return a detailed fee URL"""
    return reverse('rental_unit:fee-detail', args=[fee_id])

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

def create_fee(rental_unit_id, **params):
    """create and return a fee object"""
    defaults = {
        'name':'Pet',
        'price':Decimal('25.50'),
    }
    defaults.update(params)
    
    return Fee.objects.create(rental_unit=rental_unit_id, **defaults)
    

def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_superuser(**params):
    """create and return a new user"""
    return get_user_model().objects.create_superuser(**params)

### TEST HANDLERS ###
class PublicFeeApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_get_fee_by_non_auth(self):
        """test that unauthenticated requests can read Fees"""
        result = self.client.get(FEE_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_fee_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed fee"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        fee = create_fee(rental_unit_id=rental_unit)
        
        url = detail_url(fee.id)
        result = self.client.get(url)
        serializer = FeeDetailSerializer(fee)

        self.assertEqual(result.data, serializer.data)
        

class PrivateFeeApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_all_fees_list(self):
        """test retrieving a list of Fees"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        create_fee(rental_unit_id=rental_unit)
        create_fee(rental_unit_id=rental_unit_two)
        
        result = self.client.get(FEE_URL)
        
        fees = Fee.objects.all().order_by('-rental_unit')
        serializer = FeeSerializer(fees, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_fee_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)
        fee = create_fee(rental_unit_id=rental_unit)
        
        url = detail_url(fee.id)
        result = self.client.get(url)

        serializer = FeeDetailSerializer(fee)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_create_fee(self):
        """test error creating a Fee by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(FEE_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Fee.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_error_partial_update(self):
        """test error patch of a fee by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_price = Decimal('20')
        original_description = 'small pets only.'
        
        fee = Fee.objects.create(
            rental_unit=rental_unit,
            price=original_price,
            description=original_description, 
        )

        payload = {
            'rental_unit': fee.rental_unit.id,
            'price': Decimal('30'),
        }
        
        url = detail_url(fee.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        fee.refresh_from_db()
        self.assertEqual(fee.price, original_price)
        
    def test_error_full_update(self):
        """test error put of fee by non admin"""
        rental_unit = create_rental_unit(user=self.user)
        original_price = Decimal('20')
        original_description = 'small pets only.'
        original_name = 'Pet'
    
        fee = Fee.objects.create(
            rental_unit=rental_unit,
            price=original_price,
            description=original_description,
            name=original_name,
        )
        
        payload = {
            'rental_unit':rental_unit.id,
            'price': Decimal('30'),
            'name': 'Transport',
            'description': 'pickup and dropoff'
        }
        url = detail_url(fee.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        fee.refresh_from_db()
        
        self.assertEqual(fee.price, original_price)
        
    def test_error_delete_fee(self):
        """test error when deleting a Fee by a non admin"""
        rental_unit = create_rental_unit(user=self.user)
        fee = create_fee(rental_unit_id=rental_unit)
        
        url = detail_url(fee.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Fee.objects.filter(id=fee.id).exists())
        
        
class AdminFeeApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_fee(self):
        """test creating a Fee by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
            'name': 'Transport'
        }
        result = self.client.post(FEE_URL, payload)

        self.assertTrue(Fee.objects.filter(rental_unit=payload['rental_unit'], name=payload['name']).exists())
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        
    def test_error_create_double_fee(self):
        """test that there can only be one type of fee for one rental unit"""
        rental_unit = create_rental_unit(user=self.user)
        fee = Fee.objects.create(
            rental_unit=rental_unit,
            name='Pet',
            price=Decimal('50.51')
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'name': 'Pet',
            'price': Decimal('50.50')
        }
        result = self.client.post(FEE_URL, payload)
        
        self.assertEqual(fee.price, Decimal('50.51'))
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Fee.objects.filter(rental_unit=payload['rental_unit'], name=payload['name'], price=payload['price']).exists())
        
        
    def test_partial_update(self):
        """test patch of a fee by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_price = Decimal('20')
        original_description = 'small pets only.'
        
        fee = Fee.objects.create(
            rental_unit=rental_unit,
            price=original_price,
            description=original_description, 
        )

        payload = {
            'rental_unit': fee.rental_unit.id,
            'price': Decimal('30'),
        }
        
        url = detail_url(fee.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        fee.refresh_from_db()
        self.assertEqual(fee.price, payload['price'])
        self.assertEqual(fee.description, original_description)
        
    def test_full_update(self):
        """test put of fee"""
        rental_unit = create_rental_unit(user=self.user)
        original_price = Decimal('20')
        original_description = 'small pets only.'
        original_name = 'Pet'
    
        fee = Fee.objects.create(
            rental_unit=rental_unit,
            price=original_price,
            description=original_description,
            name=original_name,
        )
        
        payload = {
            'rental_unit':rental_unit.id,
            'price': Decimal('30'),
            'name': 'Transport',
            'description': 'pickup and dropoff'
        }
        url = detail_url(fee.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        fee.refresh_from_db()
        
        for k, v in payload.items():
            if k == 'rental_unit':
                continue
            self.assertEqual(getattr(fee, k), v)
        
    def test_delete_fee(self):
        """test deleting a Fee is successful"""
        rental_unit = create_rental_unit(user=self.user)
        fee = create_fee(rental_unit_id=rental_unit)
        
        url = detail_url(fee.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Fee.objects.filter(id=fee.id).exists())