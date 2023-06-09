"""
tests for reservation API
"""
from decimal import Decimal
from datetime import datetime, timezone, date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, Reservation, CalendarEvent, Availability

from rental_unit.serializers import (
    ReservationSerializer,
    ReservationDetailSerializer
)


RESERVATION_URL = reverse('rental_unit:reservation-list')

def detail_url(reservation_id):
    """create and return a detailed reservation URL"""
    return reverse('rental_unit:reservation-detail', args=[reservation_id])

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
class PublicRentalUnitApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(RESERVATION_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateReservationApiTests(TestCase):
    """tests for authenticated users"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_reservation(self):
        """test a user creating a reservation"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 24),
            'check_out': date(2023, 8, 30)
        }
        result = self.client.post(RESERVATION_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        
    def test_get_reservation_list_for_user(self):
        """test retrieving a list of reservations for current_user"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        rental_unit_three = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        availability_two = Availability.objects.create(rental_unit=rental_unit_two)
        availability_three = Availability.objects.create(rental_unit=rental_unit_three)

        
        guest = create_user(
            email='guest1@example.com',
            password='pass1234'
        )
        guest_two = create_user(
            email='guest2@example.com',
            password='pass1234'
        )
        
        res_one = create_reservation(user_id=guest, rental_unit_id=rental_unit)
        res_two = create_reservation(user_id=guest_two, rental_unit_id=rental_unit_two)
        res_three = create_reservation(user_id=self.user, rental_unit_id=rental_unit_three)
        result = self.client.get(RESERVATION_URL)
        
        reservation_list = Reservation.objects.filter(user=self.user).order_by('-rental_unit')
        serializer = ReservationSerializer(reservation_list, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_reservation_detail(self):
        """test get reservation detail"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        reservation = create_reservation(user_id=self.user, rental_unit_id=rental_unit)
        
        url = detail_url(reservation.id)
        result = self.client.get(url)

        serializer = ReservationDetailSerializer(reservation)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_get_other_user_reservation_detail(self):
        """test error if getting another user's reservation detail"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        other_user = create_user(
            email='testother@example.com',
            password='pass1234'
        )
        other_reservation = create_reservation(user_id=other_user, rental_unit_id=rental_unit)
        
        url = detail_url(other_reservation.id)
        result = self.client.get(url)

        self.assertTrue(result.status_code, status.HTTP_403_FORBIDDEN)
      
    def test_error_check_out_before_check_in(self):
        """test an error if a ckeck out date for a reservation is before check in date"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 24),
            'check_out': date(2023, 8, 23)
        }
        
        result = self.client.post(RESERVATION_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        
    def test_error_create_double_reservation(self):
        """test error when two or more reservations dates are not unique"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        payload_one = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 24),
            'check_out': date(2023, 8, 30)
        }
        payload_two = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 23),
            'check_out': date(2023, 8, 31)
        }
        
        result_one = self.client.post(RESERVATION_URL, payload_one)
        result_two = self.client.post(RESERVATION_URL, payload_two)
        
        self.assertEqual(result_one.status_code, status.HTTP_201_CREATED)
        self.assertEqual(result_two.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Reservation.objects.filter(
            rental_unit=payload_one['rental_unit'], 
            user=payload_one['user'],
            check_in=payload_one['check_in'],
            check_out=payload_one['check_out']
        ).exists())
        self.assertFalse(Reservation.objects.filter(
            rental_unit=payload_two['rental_unit'], 
            user=payload_two['user'],
            check_in=payload_two['check_in'],
            check_out=payload_two['check_out']
        ).exists())
        
    def test_error_reserve_on_blocked_dates(self):
        """test an error when trying to reserve for a blocked period"""
        rental_unit = create_rental_unit(user=self.user)
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit, 
            reason='Blocked',
            start_date=date(2023, 8, 2),
            end_date=date(2023, 8, 6)
        )
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 6)
        }
        
        result = self.client.post(RESERVATION_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        
    def test_error_reservation_too_short(self):
        """check that a reservation length is not shorter than minimum stay"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(
            rental_unit=rental_unit,
            min_stay=2
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 3)
        }
        
        result = self.client.post(RESERVATION_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        
    def test_error_reservation_too_long(self):
        """check that a reservation length is not greater than maximum stay"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(
            rental_unit=rental_unit,
            max_stay=20
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 30),
        }
        
        result = self.client.post(RESERVATION_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        
    def test_error_reservation_made_too_late(self):
        """test error when creating a reservation after min notice"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(
            rental_unit=rental_unit,
            min_notice=5
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 6, 11),
            'check_out': date(2023, 6, 15),
        }
        
        result = self.client.post(RESERVATION_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        
    def test_error_reservation_made_too_early(self):
        """test error when creating a reservation before max notice"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(
            rental_unit=rental_unit,
            max_notice=365
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2024, 6, 11),
            'check_out': date(2024, 6, 15),
        }
        
        result = self.client.post(RESERVATION_URL, payload)
        print(result.content)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())