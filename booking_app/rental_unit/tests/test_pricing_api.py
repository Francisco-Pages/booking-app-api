"""
tests for Pricing API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, Pricing

from rental_unit.serializers import (
    PricingSerializer,
    PricingDetailSerializer
)


PRICING_URL = reverse('rental_unit:pricing-list')

## HELPER FUNCTIONS
def detail_url(pricing_id):
    """create and return a detailed pricing URL"""
    return reverse('rental_unit:pricing-detail', args=[pricing_id])

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
class PublicPricingApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_get_pricing_by_non_auth(self):
        """test that unauthenticated requests can read pricing details"""
        result = self.client.get(PRICING_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_pricing_by_non_auth(self):
        """test that unauthenticated requests can read Pricing details"""
        result = self.client.get(PRICING_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_pricing_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed pricing"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
        url = detail_url(pricing.rental_unit.id)
        result = self.client.get(url)
        serializer = PricingDetailSerializer(pricing)
        self.assertEqual(result.data, serializer.data)
        
        
class PrivatePricingApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_all_pricing(self):
        """test that authenticated requests can read Pricing details"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        Pricing.objects.create(rental_unit=rental_unit)
        Pricing.objects.create(rental_unit=rental_unit_two)
        
        result = self.client.get(PRICING_URL)

        pricing_list = Pricing.objects.all().order_by('-rental_unit')
        serializer = PricingSerializer(pricing_list, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_pricing_detail(self):
        """test that an authenticated request can read a detailed pricing"""
        rental_unit = create_rental_unit(user=self.user)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
        url = detail_url(pricing.rental_unit.id)
        result = self.client.get(url)
        
        serializer = PricingDetailSerializer(pricing)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_create_pricing(self):
        """test error when creating a pricing by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(PRICING_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Pricing.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_error_partial_update(self):
        """test error patch of a pricing by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_night_price = Decimal('150.99')
        original_currency = 'BIT'
        
        pricing = Pricing.objects.create(
            rental_unit=rental_unit, 
            night_price=original_night_price,
            currency=original_currency
        )

        payload = {
            'rental_unit':pricing.rental_unit.id,
            'night_price': Decimal('200.99')
        }
        
        url = detail_url(pricing.rental_unit.id)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        pricing.refresh_from_db()
        self.assertEqual(pricing.night_price, original_night_price)
        self.assertEqual(pricing.currency, original_currency)
        
    def test_error_full_update(self):
        """test error of put of pricing"""
        rental_unit = create_rental_unit(user=self.user)
        
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': pricing.rental_unit.id,
            'night_price': Decimal('100.99'),
            'smart_pricing': True,
            'min_price': Decimal('100'),
            'max_price': Decimal('150'),
            'currency': 'YEN',
            'week_discount': 10,
            'month_discount': 15,
            'tax': Decimal('7.00'),
        }
        
        url = detail_url(pricing.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        pricing.refresh_from_db()
        # flag = 0
        # for k, v in original_values.items():
        #     flag += 1
        #     if flag == 1:
        #         continue
        #     self.assertEqual(getattr(pricing, k), v)

    def test_error_delete_pricing(self):
        """test error deleting a pricing by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
        url = detail_url(pricing.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Pricing.objects.filter(rental_unit=pricing.rental_unit.id).exists())
        
        
class AdminPricingApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_pricing(self):
        """test creating a Pricing by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(PRICING_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Pricing.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_partial_update(self):
        """test patch of a pricing by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_night_price = Decimal('150.99')
        original_currency = 'BIT'
        
        pricing = Pricing.objects.create(
            rental_unit=rental_unit, 
            night_price=original_night_price,
            currency=original_currency
        )

        payload = {
            'rental_unit':pricing.rental_unit.id,
            'night_price': Decimal('200.99')
        }
        
        url = detail_url(pricing.rental_unit.id)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        pricing.refresh_from_db()
        self.assertEqual(pricing.night_price, payload['night_price'])
        self.assertEqual(pricing.currency, original_currency)
        
    def test_full_update(self):
        """test put of pricing"""
        rental_unit = create_rental_unit(user=self.user)
        
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': pricing.rental_unit.id,
            'night_price': Decimal('100.99'),
            'smart_pricing': True,
            'min_price': Decimal('100'),
            'max_price': Decimal('150'),
            'currency': 'YEN',
            'week_discount': 10,
            'month_discount': 15,
            'tax': Decimal('7.00'),
        }
        
        url = detail_url(pricing.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        pricing.refresh_from_db()
        flag = 0
        for k, v in payload.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(pricing, k), v)
        
    def test_delete_pricing(self):
        """test deleting a pricing is successful"""
        rental_unit = create_rental_unit(user=self.user)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
        url = detail_url(pricing.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Pricing.objects.filter(rental_unit=pricing.rental_unit.id).exists())