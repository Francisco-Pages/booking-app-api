"""
tests for image API
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

from core.models import RentalUnit, Photo

from rental_unit.serializers import (PhotoSerializer)


PHOTO_URL = reverse('rental_unit:photo-list')

## HELPER FUNCTIONS
def detail_url(photo_id):
    """create and return a detailed rental unit URL"""
    return reverse('rental_unit:photo-detail', args=[photo_id])

def photo_upload_url(photo_id):
    """create and return an image upload URL"""
    return reverse('rental_unit:photo-upload-image', args=[photo_id])

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

class PhotoUploadTests(TestCase):
    """tests for image upload API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.rental_unit = create_rental_unit(user=self.user)
        self.photo = Photo.objects.create(
            rental_unit=self.rental_unit
        )
        
    def tearDown(self):
        self.photo.image.delete()
        
    def test_upload_image(self):
        url = photo_upload_url(self.photo.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {
                'rental_unit': self.rental_unit,
                'image': image_file
            }
            res = self.client.post(url, payload, format='multipart')

        self.photo.refresh_from_db()
        
        for photo in Photo.objects.all():
            print(self.photo.__dict__)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.photo.image.path))

    def test_upload_image_bad_request(self):
        url = photo_upload_url(self.photo.id)

        payload = {
            'rental_unit': self.rental_unit.id,
            'image': 'notanimage'
        }
        res = self.client.post(url, payload, format='multipart')
            
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)