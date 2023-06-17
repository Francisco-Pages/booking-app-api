"""
tests for reservation_request API
"""
from decimal import Decimal
from datetime import datetime, timezone, date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, ReservationRequest, CalendarEvent, Availability, Pricing, Reservation, CancellationRequest

from rental_unit.serializers import (
    CancellationRequestSerializer,
    CancellationRequestDetailSerializer
)


CANCELLATION_REQUEST_URL = reverse('rental_unit:cancellationrequest-list')

def detail_url(cancellation_request_id):
    """create and return a detailed reservation_request URL"""
    return reverse('rental_unit:cancellationrequest-detail', args=[cancellation_request_id])

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

def create_reservation(user_id, rental_unit_id, **params):
    """create and return a reservation"""
    defaults = {
        'check_in': date(2023, 8, 24),
        'check_out': date(2023, 8, 30)
    }
    defaults.update(params)
    
    reservation = Reservation.objects.create(user=user_id, rental_unit=rental_unit_id, **defaults)
    return reservation

def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_superuser(**params):
    """create and return a new user"""
    return get_user_model().objects.create_superuser(**params)


### TEST HANDLERS ###
class PublicCancellationRequestApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(CANCELLATION_REQUEST_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class PrivateCancellationRequestApiTests(TestCase):
    """tests for authenticated API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_cancellation_request(self):
        """create a cancellation request"""
        rental_unit = create_rental_unit(user=self.user)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        self.assertTrue(Reservation.objects.filter(id=reservation.id).exists())
        payload = {
            'user': self.user.id,
            'reservation': reservation.id,
        }
        
        result = self.client.post(CANCELLATION_REQUEST_URL, payload)
        
        self.assertTrue(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CancellationRequest.objects.filter(reservation=reservation).exists())

    def test_get_cancellation_request_list_for_user(self):
        """test retrieving a list of cancellations for current_user"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        rental_unit_three = create_rental_unit(user=self.user)
        
        guest = create_user(
            email='guest1@example.com',
            password='pass1234'
        )
        
        res_one = create_reservation(user_id=guest, rental_unit_id=rental_unit)
        res_two = create_reservation(user_id=self.user, rental_unit_id=rental_unit_two)
        res_three = create_reservation(user_id=self.user, rental_unit_id=rental_unit_three)
       
        cr_two = CancellationRequest.objects.create(
            user=self.user,
            reservation=res_two
        )
        cr_three = CancellationRequest.objects.create(
            user=self.user,
            reservation=res_three
        )

        result = self.client.get(CANCELLATION_REQUEST_URL)
        
        cancellation_request_list = CancellationRequest.objects.filter(user=self.user).order_by('-creation_date')
        serializer = CancellationRequestSerializer(cancellation_request_list, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_cancellation_request_detail(self):
        """test getting a detailed cancellation request"""
        rental_unit = create_rental_unit(user=self.user)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        cancellation_request = CancellationRequest.objects.create(user=self.user, reservation=reservation)
        
        url = detail_url(cancellation_request.id)
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        serializer = CancellationRequestDetailSerializer(cancellation_request)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_update_cancellation_request(self):
        """test error when user tries to update a cancellation request"""
        rental_unit = create_rental_unit(user=self.user)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        cancellation_request = CancellationRequest.objects.create(
            user=self.user,
            reservation=reservation
        )
        new_status = True
        
        payload = {
            'rental_unit': rental_unit.id,
            'status': new_status
        }
        
        url = detail_url(cancellation_request.id)
        result = self.client.patch(url, payload)
        
        cancellation_request.refresh_from_db()
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(cancellation_request.status, False)
        
    def test_delete_cancellation_request(self):
        """test a user deleting a cancellation request"""
        rental_unit = create_rental_unit(user=self.user)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        cancellation_request = CancellationRequest.objects.create(
            user=self.user,
            reservation=reservation
        )
        
        url = detail_url(cancellation_request.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CancellationRequest.objects.filter(id=cancellation_request.id).exists())
    
class AdminCancellationRequestApiTests(TestCase):
    """tests for administrative API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='supertest@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_update_cancellation_request(self):
        """test error when user tries to update a cancellation request"""
        rental_unit = create_rental_unit(user=self.user)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        cancellation_request = CancellationRequest.objects.create(
            user=self.user,
            reservation=reservation
        )
        new_status = True
        
        payload = {
            'rental_unit': rental_unit.id,
            'status': new_status
        }
        
        url = detail_url(cancellation_request.id)
        result = self.client.patch(url, payload)
        
        cancellation_request.refresh_from_db()
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(cancellation_request.status, new_status)