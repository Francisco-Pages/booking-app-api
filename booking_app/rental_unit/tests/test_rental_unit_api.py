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
class PublicRentalUnitApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(RENTAL_UNIT_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRentalUnitApiTests(TestCase):
    """test for authenticated API requests."""

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

    def test_get_rental_unit_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)

        url = detail_url(rental_unit.id)
        result = self.client.get(url)

        serializer = RentalUnitDetailSerializer(rental_unit)
        self.assertEqual(result.data, serializer.data)        

    def test_error_create_rental_unit(self):
        """test error creating a rental unit by a non administrator"""
        payload = {
            'user': self.user,
            'title':'Title of property not created by an administrator',
        }
        result = self.client.post(RENTAL_UNIT_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(RentalUnit.objects.filter(title=payload['title']).exists())
        
    def test_error_partial_update(self):
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
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        rental_unit.refresh_from_db()
        self.assertNotEqual(rental_unit.title, payload['title'])
        self.assertEqual(rental_unit.link, original_link)
        self.assertEqual(rental_unit.user, self.user)

    def test_error_full_update(self):
        """test put of rental unit"""
        original_title = 'sample unit title'
        rental_unit = create_rental_unit(
            user=self.user,
            title=original_title,
            description='sample unit description',
        )

        payload = {
            'title': 'NEW Title of property',
            'description': 'NEW A unique description of your home',
            'link': 'https://example.com/new-rental-unit.pdf',
            'languages': 'vi',
            'status': 'Active',
            'images': 'NEW images',
            'unit_type': 'Hotel',
            'max_guests': 1,
        }
        url = detail_url(rental_unit.id)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        rental_unit.refresh_from_db()
        self.assertEqual(rental_unit.title, original_title)
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

    def test_error_delete_rental_unit(self):
        """test error deleting a rental unit if not administrator"""
        rental_unit = create_rental_unit(user=self.user)

        url = detail_url(rental_unit.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(RentalUnit.objects.filter(id=rental_unit.id).exists())


class AdminRentalUnitApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_rental_unit(self):
        """test creating a rental unit by an administrator"""
        payload = {
            'user': self.user,
            'title':'Title of property created by an administrator',
        }
        result = self.client.post(RENTAL_UNIT_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(RentalUnit.objects.filter(title=payload['title']).exists())

    def test_partial_update(self):
        """test patch of a rental unit"""
        original_link = 'https://example.com/rental-unit.pdf'
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
            description='sample unit description',
        )

        payload = {
            'title': 'NEW Title of property',
            'description': 'NEW A unique description of your home',
            'link': 'https://example.com/new-rental-unit.pdf',
            'languages': 'vi',
            'status': 'Active',
            'images': 'NEW images',
            'unit_type': 'Hotel',
            'max_guests': 1,
        }
        url = detail_url(rental_unit.id)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        rental_unit.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(rental_unit, k), v)
        self.assertEqual(rental_unit.user, self.user)
        
    def test_delete_rental_unit(self):
        """test deleting a rental unit"""
        rental_unit = create_rental_unit(user=self.user)

        url = detail_url(rental_unit.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RentalUnit.objects.filter(id=rental_unit.id).exists())