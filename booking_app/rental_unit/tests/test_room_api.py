"""
tests for room API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, Room

from rental_unit.serializers import (
    RoomSerializer,
    RoomDetailSerializer
)


ROOM_URL = reverse('rental_unit:room-list')

def detail_url(room_id):
    """create and return a detailed room URL"""
    return reverse('rental_unit:room-detail', args=[room_id])

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
class PublicRoomApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_get_room_by_non_auth(self):
        """test that unauthenticated requests can read Rooms"""
        result = self.client.get(ROOM_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_room_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed room"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        room = Room.objects.create(rental_unit=rental_unit)
        
        url = detail_url(room.rental_unit.id)
        result = self.client.get(url)
        serializer = RoomDetailSerializer(room)

        self.assertEqual(result.data, serializer.data)
        

class PrivateRoomApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_all_rooms_list(self):
        """test retrieving a list of Rooms"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        Room.objects.create(rental_unit=rental_unit)
        Room.objects.create(rental_unit=rental_unit_two)
        
        result = self.client.get(ROOM_URL)
        
        room = Room.objects.all().order_by('-rental_unit')
        serializer = RoomSerializer(room, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_room_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)
        room = Room.objects.create(rental_unit=rental_unit)
        
        url = detail_url(room.rental_unit.id)
        result = self.client.get(url)

        serializer = RoomDetailSerializer(room)
        self.assertEqual(result.data, serializer.data)
        