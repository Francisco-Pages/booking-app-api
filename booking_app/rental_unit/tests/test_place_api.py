"""
tests for place API
"""
from decimal import Decimal
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, Place

from rental_unit.serializers import (
    PlaceSerializer,
    PlaceDetailSerializer
)


PLACE_URL = reverse('rental_unit:place-list')

def detail_url(place_id):
    """create and return a detailed place URL"""
    return reverse('rental_unit:place-detail', args=[place_id])

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
class PublicPlaceApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_get_place_by_non_auth(self):
        """test that unauthenticated requests can read Places"""
        result = self.client.get(PLACE_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_place_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed place"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        place = Place.objects.create(rental_unit=rental_unit)
        
        url = detail_url(place.id)
        result = self.client.get(url)
        serializer = PlaceDetailSerializer(place)

        self.assertEqual(result.data, serializer.data)
        

class PrivatePlaceApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_all_places_list(self):
        """test retrieving a list of Places"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        Place.objects.create(
            rental_unit=rental_unit_two,
            name='Chinois',
            category='Restaurant'
        )
        Place.objects.create(
            rental_unit=rental_unit,
            name='Punto Italia',
            category='Restaurant'    
        )
        
        result = self.client.get(PLACE_URL)
        
        places = Place.objects.all().order_by('-category')
        serializer = PlaceSerializer(places, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_place_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)
        place = Place.objects.create(rental_unit=rental_unit)
        
        url = detail_url(place.id)
        result = self.client.get(url)

        serializer = PlaceDetailSerializer(place)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_create_place(self):
        """test error creating a Place by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
            'name': 'Chinois',
            'category': "Restaurant",
        }
        
        result = self.client.post(PLACE_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Place.objects.filter(name=payload['name']).exists())
        
    # def test_error_partial_update(self):
    #     """test error patch of a place by a non administrator"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     original_reason = 'Blocked'
    #     original_notes = 'sample notes'
        
    #     place = Place.objects.create(
    #         rental_unit=rental_unit,
    #         reason=original_reason,
    #         notes=original_notes, 
    #     )

    #     payload = {
    #         'rental_unit': rental_unit.id,
    #         'reason': 'Reservation',
    #         'notes': f'reservation updated for unit #{rental_unit.id}'
    #     }
        
    #     url = detail_url(place.id)
    #     result = self.client.patch(url, payload)
        
    #     self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
    #     place.refresh_from_db()
    #     self.assertEqual(place.reason, original_reason)
    #     self.assertEqual(place.notes, original_notes)
        
    # def test_error_full_update(self):
    #     """test error put of place by non admin"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     original_reason = 'Blocked'
    #     original_start = '2023-06-28T12:38:30.756209Z'
    #     original_end = '2023-07-4T12:38:30.756209Z'
    #     original_notes = f"reservation for rental unit #{rental_unit.id}"
        
        
    #     place = Place.objects.create(
    #         rental_unit=rental_unit,
    #         reason=original_reason,
    #         start_date=original_start,
    #         end_date=original_end,
    #         notes=original_notes, 
    #     )

    #     payload = {
    #         'id': place.id,
    #         'reason': 'Reservation',
    #         'start_date': datetime(2023,6,20,12,38,30, tzinfo=timezone.utc),
    #         'end_date': datetime(2023,6,27,12,38,30, tzinfo=timezone.utc),
    #         'notes': f'reservation updated for unit #{rental_unit.id}'
    #     }
        
    #     url = detail_url(place.id)
        
    #     result = self.client.put(url, payload)

    #     self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
    #     place.refresh_from_db()

    #     self.assertEqual(getattr(place, 'notes'), original_notes)
        
    def test_error_delete_place(self):
        """test error when deleting a Place by a non admin"""
        rental_unit = create_rental_unit(user=self.user)
        place = Place.objects.create(rental_unit=rental_unit)
        
        url = detail_url(place.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Place.objects.filter(id=place.id).exists())
        
        
class AdminPlaceApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_place(self):
        """test creating a Place by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
            'name': 'Chinois',
            'category': "Restaurant",
        }
        result = self.client.post(PLACE_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Place.objects.filter(name=payload['name']).exists())

    # def test_error_create_double_place(self):
    #     """test that there can only be one type of place for one rental unit"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     place = Place.objects.create(
    #         rental_unit=rental_unit,
    #         name='Pet',
    #         price=Decimal('50.51')
    #     )
        
    #     payload = {
    #         'rental_unit': rental_unit.id,
    #         'name': 'Pet',
    #         'price': Decimal('50.50')
    #     }
    #     result = self.client.post(PLACE_URL, payload)
        
    #     self.assertEqual(place.price, Decimal('50.51'))
    #     self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertFalse(Place.objects.filter(rental_unit=payload['rental_unit'], name=payload['name'], price=payload['price']).exists())
           
    # def test_partial_update(self):
    #     """test patch of a place by an administrator"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     original_reason = 'Blocked'
    #     original_notes = 'sample notes'
        
    #     place = Place.objects.create(
    #         rental_unit=rental_unit,
    #         reason=original_reason,
    #         notes=original_notes, 
    #     )

    #     payload = {
    #         'rental_unit': rental_unit.id,
    #         'reason': 'Reservation',
    #         'notes': f'reservation updated for unit #{rental_unit.id}'
    #     }
        
    #     url = detail_url(place.id)
    #     result = self.client.patch(url, payload)
        
    #     self.assertEqual(result.status_code, status.HTTP_200_OK)
    #     place.refresh_from_db()
    #     self.assertEqual(place.reason, payload['reason'])
    #     self.assertEqual(place.notes, payload['notes'])
        
    # def test_full_update(self):
    #     """test put of place"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     original_reason = 'Blocked'
    #     original_start = '2023-06-28T12:38:30.756209Z'
    #     original_end = '2023-07-4T12:38:30.756209Z'
    #     original_notes = f"reservation for rental unit #{rental_unit.id}"
        
        
    #     place = Place.objects.create(
    #         rental_unit=rental_unit,
    #         reason=original_reason,
    #         start_date=original_start,
    #         end_date=original_end,
    #         notes=original_notes, 
    #     )

    #     payload = {
    #         'id': place.id,
    #         'reason': 'Reservation',
    #         'start_date': datetime(2023,6,20,12,38,30, tzinfo=timezone.utc),
    #         'end_date': datetime(2023,6,27,12,38,30, tzinfo=timezone.utc),
    #         'notes': f'reservation updated for unit #{rental_unit.id}'
    #     }
        
    #     url = detail_url(place.id)
        
    #     result = self.client.put(url, payload)

    #     self.assertEqual(result.status_code, status.HTTP_200_OK)
    #     place.refresh_from_db()
        
    #     for k, v in payload.items():
    #         if k == 'rental_unit':
    #             continue
    #         self.assertEqual(getattr(place, k), v)
        
    def test_delete_place(self):
        """test deleting a Place is successful"""
        rental_unit = create_rental_unit(user=self.user)
        place = Place.objects.create(rental_unit=rental_unit)
        
        url = detail_url(place.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Place.objects.filter(id=place.id).exists())