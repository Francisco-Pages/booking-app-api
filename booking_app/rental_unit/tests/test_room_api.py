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
        'status':False,
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
        
    def test_error_create_room(self):
        """test error creating a Room by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(ROOM_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Room.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_partial_update(self):
        """test error patch of a room by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_name = 'scarface bathroom'
        original_room_type = 'bathroom'
        
        room = Room.objects.create(
            rental_unit=rental_unit, 
            name=original_name,
            room_type=original_room_type
        )

        payload = {
            'rental_unit': room.rental_unit.id,
            'name': 'a new name',
            'room_type': 'bedroom'
        }
        
        url = detail_url(room.rental_unit.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        room.refresh_from_db()
        self.assertEqual(room.room_type, original_room_type)
        self.assertEqual(room.name, original_name)
        
    def test_error_full_update(self):
        """test error when put of Room done by non admin"""
        rental_unit = create_rental_unit(user=self.user)
        room = Room.objects.create(
            rental_unit=rental_unit,
            name='default',
            room_type='half bathroom',
            bed_type='',
            tv=True,
            accessible= False,
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'name': 'new name',
            'room_type': 'bathroom',
            'bed_type': '',
            'tv': True,
            'accessible': False,
        }
        url = detail_url(room.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        # room.refresh_from_db()
        # flag = 0
        # for k, v in payload.items():
        #     flag += 1
        #     if flag == 1:
        #         continue
        #     self.assertEqual(getattr(room, k), v)
        
    def test_error_delete_room(self):
        """test error when deleting a Room by a non admin"""
        rental_unit = create_rental_unit(user=self.user)
        room = Room.objects.create(rental_unit=rental_unit)
        
        url = detail_url(room.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Room.objects.filter(rental_unit=room.rental_unit.id).exists())
        
class AdminRoomApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_room(self):
        """test creating a Room by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
        }
        result = self.client.post(ROOM_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Room.objects.filter(rental_unit=payload['rental_unit']).exists())
        
    def test_partial_update(self):
        """test patch of a room by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_name = 'scarface bathroom'
        original_room_type = 'bathroom'
        
        room = Room.objects.create(
            rental_unit=rental_unit, 
            name=original_name,
            room_type=original_room_type
        )

        payload = {
            'rental_unit': room.rental_unit.id,
            'name': 'a new name'
        }
        
        url = detail_url(room.rental_unit.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        room.refresh_from_db()
        self.assertEqual(room.room_type, original_room_type)
        self.assertEqual(room.name, payload['name'])
        
    def test_full_update(self):
        """test put of Room"""
        rental_unit = create_rental_unit(user=self.user)
        room = Room.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': room.rental_unit.id,
            'name': 'new name',
            'room_type': 'Bedroom',
            'bed_type': 'King',
            'tv': True,
            'accessible': False,
        }
        url = detail_url(room.rental_unit.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        room.refresh_from_db()
        flag = 0
        for k, v in payload.items():
            flag += 1
            if flag == 1:
                continue
            self.assertEqual(getattr(room, k), v)
            
    def test_delete_room(self):
        """test deleting a Room is successful"""
        rental_unit = create_rental_unit(user=self.user)
        room = Room.objects.create(rental_unit=rental_unit)
        
        url = detail_url(room.rental_unit.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Room.objects.filter(rental_unit=room.rental_unit.id).exists())