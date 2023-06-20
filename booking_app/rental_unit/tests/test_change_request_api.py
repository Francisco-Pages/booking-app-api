"""
tests for change_request API
"""
from decimal import Decimal
from datetime import datetime, timezone, date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, ChangeRequest, CalendarEvent, Availability, Pricing, Reservation, Rulebook

from rental_unit.serializers import (
    ChangeRequestSerializer,
    ChangeRequestDetailSerializer
)

now = datetime.now().date()


CHANGE_REQUEST_URL = reverse('rental_unit:changerequest-list')

def detail_url(change_request_id):
    """create and return a detailed change_request URL"""
    return reverse('rental_unit:changerequest-detail', args=[change_request_id])

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
        'check_out': date(2023, 8, 30),
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
class PublicChangeRequestApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(CHANGE_REQUEST_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateChangeRequestApiTests(TestCase):
    """tests for authenticated API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_change_request_list_for_user(self):
        """test retrieving a list of change for current_user"""
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
       
        cr_two = ChangeRequest.objects.create(
            user=self.user,
            reservation=res_two,
            new_check_in=now + timedelta(days=15),
            new_check_out=now + timedelta(days=19)
        )
        cr_three = ChangeRequest.objects.create(
            user=self.user,
            reservation=res_three,
            new_check_in=now + timedelta(days=25),
            new_check_out=now + timedelta(days=29)
        )

        result = self.client.get(CHANGE_REQUEST_URL)
        
        cancellation_request_list = ChangeRequest.objects.filter(user=self.user).order_by('-creation_date')
        serializer = ChangeRequestSerializer(cancellation_request_list, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_change_request_detail(self):
        """test getting a detailed change request"""
        rental_unit = create_rental_unit(user=self.user)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        change_request = ChangeRequest.objects.create(
            user=self.user,
            reservation=reservation,
            new_check_in=now + timedelta(days=35),
            new_check_out=now + timedelta(days=39)
        )
        
        url = detail_url(change_request.id)
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        serializer = ChangeRequestDetailSerializer(change_request)
        self.assertEqual(result.data, serializer.data)
        
    def test_create_change_request(self):
        """create a cancellation request"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        payload = {
            'user': self.user.id,
            'reservation': reservation.id,
            'new_check_in': now + timedelta(days=15),
            'new_check_out': now + timedelta(days=21)
        }
        
        result = self.client.post(CHANGE_REQUEST_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ChangeRequest.objects.filter(reservation=reservation).exists())
        
    def test_delete_change_request(self):
        """test deleting a change request"""
        rental_unit = create_rental_unit(user=self.user)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        change_request = ChangeRequest.objects.create(
            user=self.user,
            reservation=reservation,
            new_check_in=now + timedelta(days=15),
            new_check_out=now + timedelta(days=21)
        )
        
        self.assertTrue(ChangeRequest.objects.filter(reservation=reservation).exists())
        
        url = detail_url(change_request.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ChangeRequest.objects.filter(reservation=reservation).exists())
        
    def test_error_delete_change_request(self):
        """test error deleting a change request when it has been accepted"""
        rental_unit = create_rental_unit(user=self.user)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        change_request = ChangeRequest.objects.create(
            user=self.user,
            reservation=reservation,
            new_check_in=now + timedelta(days=15),
            new_check_out=now + timedelta(days=21),
            status=True
        )
        
        self.assertTrue(ChangeRequest.objects.filter(reservation=reservation).exists())
        
        url = detail_url(change_request.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(ChangeRequest.objects.filter(reservation=reservation).exists())
        
    def test_error_update_change_request(self):
        """test error when updating a change request"""
        rental_unit = create_rental_unit(user=self.user)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        change_request = ChangeRequest.objects.create(
            user=self.user,
            reservation=reservation,
            new_check_in=now + timedelta(days=15),
            new_check_out=now + timedelta(days=21),
            status=True
        )
        
        payload = {
            'new_check_in': now + timedelta(days=17)
        }
        
        result = self.client.patch(CHANGE_REQUEST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(ChangeRequest.objects.filter(reservation=reservation).exists())
        
    
class AdminChangeRequestApiTests(TestCase):
    """tests for administrative API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='supertest@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_update_change_request(self):
        """test updating a change request"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        pricing = Pricing.objects.create(rental_unit=rental_unit, night_price=100)
        
        check_in = now + timedelta(days=10) 
        check_out = now + timedelta(days=20)
        
        reservation = create_reservation(
            user_id=self.user, 
            rental_unit_id=rental_unit,
            check_in=check_in,
            check_out=check_out
        )
        print(reservation.check_in)
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason='Reservation',
            start_date=check_in,
            end_date=check_out
        )
        print(calendar_event)
        change_request = ChangeRequest.objects.create(
            user=self.user,
            reservation=reservation,
            new_check_in=now + timedelta(days=15),
            new_check_out=now + timedelta(days=35),
            status=False
        )
        print()
        print(reservation.total)
        payload = {
            'reservation': reservation.id,
            'user': self.user.id,
            'status': True
        }
        
        url = detail_url(change_request.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        change_request.refresh_from_db()
        self.assertTrue(ChangeRequest.objects.filter(id=change_request.id).exists())
        self.assertEqual(change_request.status, payload['status'])
        reservation.refresh_from_db()
        calendar_event.refresh_from_db()
        print()
        print(reservation.total)
        self.assertEqual(change_request.new_check_in, reservation.check_in)
        self.assertEqual(change_request.new_check_in, calendar_event.start_date)
