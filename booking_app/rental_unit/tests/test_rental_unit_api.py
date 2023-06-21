"""
tests for rental unit API
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

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

def image_upload_url(rental_unit_id):
    """create and return an image upload URL"""
    return reverse('rental_unit:rentalunit-upload-image', args=[rental_unit_id])

def create_rental_unit(user, **params):
    """create and return a rental unit object"""
    defaults = {
        'title':'Title of property',
        'description':'A unique description of your home',
        'unit_type':'apartment',
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
class PublicRentalUnitApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required(self):
        result = self.client.get(RENTAL_UNIT_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_rental_unit_by_non_auth(self):
        """test that unauthenticated requests can read amenities"""
        result = self.client.get(RENTAL_UNIT_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_location_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed location"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        
        url = detail_url(rental_unit.id)
        result = self.client.get(url)
        serializer = RentalUnitDetailSerializer(rental_unit)

        self.assertEqual(result.data, serializer.data)

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
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
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
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
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
            'user': rental_unit.user,
            'title': 'NEW Title of property',
            'description': 'NEW A unique description of your home',
            'link': 'https://example.com/new-rental-unit.pdf',
            'languages': 'vi',
            'status': True,
            'images': 'NEW images',
            'unit_type': 'Hotel',
            'max_guests': 1,
            'image': ''
        }
        url = detail_url(rental_unit.id)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
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

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
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
            'user': self.user.id,
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
            'user': rental_unit.user.id,
            'title': 'NEW Title of property',
            'description': 'NEW A unique description of your home',
            'link': 'https://example.com/new-rental-unit.pdf',
            'languages': 'vi',
            'status': True,
            'images': 'NEW images',
            'unit_type': 'Hotel',
            'max_guests': 1,
            'image': ''
        }
        url = detail_url(rental_unit.id)
        result = self.client.put(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_delete_rental_unit(self):
        """test deleting a rental unit is successful"""
        rental_unit = create_rental_unit(user=self.user)

        url = detail_url(rental_unit.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RentalUnit.objects.filter(id=rental_unit.id).exists())
        
        
class ImageUploadTests(TestCase):
    """tests for image upload API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.rental_unit = create_rental_unit(user=self.user)
        
    def tearDown(self):
        self.rental_unit.image.delete()
        
    def test_upload_image(self):
        url = image_upload_url(self.rental_unit.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')
            

        self.rental_unit.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.rental_unit.image.path))
        
    def test_upload_image_bad_request(self):
        url = image_upload_url(self.rental_unit.id)

        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')
            
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)