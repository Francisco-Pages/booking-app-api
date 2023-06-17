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

from core.models import RentalUnit, ReservationRequest, CalendarEvent, Availability, Pricing, Reservation

from rental_unit.serializers import (
    ReservationRequestSerializer,
    ReservationRequestDetailSerializer
)


RESERVATION_REQUEST_URL = reverse('rental_unit:reservationrequest-list')
RESERVATION_URL = reverse('rental_unit:reservation-list')

def detail_url(reservation_request_id):
    """create and return a detailed reservation_request URL"""
    return reverse('rental_unit:reservationrequest-detail', args=[reservation_request_id])

def reservation_detail_url(reservation_id):
    """create and return a detailed reservation_request URL"""
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

def create_reservation_request(user_id, rental_unit_id, **params):
    """create and return a reservation_request"""
    defaults = {
        'check_in': date(2023, 8, 24),
        'check_out': date(2023, 8, 30)
    }
    defaults.update(params)
    
    reservation_request = ReservationRequest.objects.create(user=user_id, rental_unit=rental_unit_id, **defaults)
    return reservation_request

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
        result = self.client.get(RESERVATION_REQUEST_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateReservationRequestApiTests(TestCase):
    """tests for authenticated users"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_reservation_request(self):
        """test a user creating a reservation request"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 24),
            'check_out': date(2023, 8, 30)
        }
        result = self.client.post(RESERVATION_REQUEST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ReservationRequest.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        
    def test_get_reservation_request_list_for_user(self):
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
        
        res_one = create_reservation_request(user_id=guest, rental_unit_id=rental_unit)
        res_two = create_reservation_request(user_id=self.user, rental_unit_id=rental_unit_two)
        res_three = create_reservation_request(user_id=self.user, rental_unit_id=rental_unit_three)
       
        result = self.client.get(RESERVATION_REQUEST_URL)
        
        reservation_list = ReservationRequest.objects.filter(user=self.user).order_by('-check_in')
        serializer = ReservationRequestSerializer(reservation_list, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_reservation_request_detail(self):
        """test get reservation request detail"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        reservation_request = create_reservation_request(user_id=self.user, rental_unit_id=rental_unit)
        
        url = detail_url(reservation_request.id)
        result = self.client.get(url)

        serializer = ReservationRequestDetailSerializer(reservation_request)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_get_other_user_reservation_detail(self):
        """test error if getting another user's reservation request detail"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        
        other_user = create_user(
            email='testother@example.com',
            password='pass1234'
        )
        other_reservation_request = create_reservation_request(user_id=other_user, rental_unit_id=rental_unit)
        
        url = detail_url(other_reservation_request.id)
        result = self.client.get(url)

        self.assertTrue(result.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_error_patch_reservation_request(self):
        """test error when a non admin user patches a reservation request"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
        original_check_out = date(2023, 9, 30)
        
        reservation_request = create_reservation_request(
            user_id=self.user, 
            rental_unit_id=rental_unit,
            check_in=date(2023, 9, 24),
            check_out=original_check_out
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'check_out': date(2023, 10, 1)
        }
        
        url = detail_url(reservation_request.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(reservation_request.check_out, original_check_out)
        
    def test_error_delete_reservation_request(self):
        """test non admin deleting a reservation request"""
        rental_unit = create_rental_unit(user=self.user)
        reservation_request = create_reservation_request(user_id=self.user, rental_unit_id=rental_unit)
        
        url = detail_url(reservation_request.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(ReservationRequest.objects.filter(id=reservation_request.id).exists())
        
    def test_error_check_out_before_check_in(self):
        """test an error if a ckeck out date for a reservation is before check in date"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 24),
            'check_out': date(2023, 8, 23)
        }
        
        result = self.client.post(RESERVATION_REQUEST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ReservationRequest.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        
    def test_error_create_double_reservation_from_request(self):
        """test error when two or more reservations dates are not unique"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit, instant_booking=True)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        
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
        
        result_one = self.client.post(RESERVATION_REQUEST_URL, payload_one)
        result_two = self.client.post(RESERVATION_REQUEST_URL, payload_two)
        
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
        
    def test_error_create_reservation_request_on_blocked_dates(self):
        """test an error when trying to reserve for a blocked period"""
        rental_unit = create_rental_unit(user=self.user)
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit, 
            reason='Blocked',
            start_date=date(2023, 8, 2),
            end_date=date(2023, 8, 6)
        )
        availability = Availability.objects.create(rental_unit=rental_unit, instant_booking=True)
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 6)
        }
        
        result = self.client.post(RESERVATION_REQUEST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        self.assertFalse(ReservationRequest.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())

    def test_error_reservation_too_short(self):
        """check that a reservation length is not shorter than minimum stay"""
        rental_unit = create_rental_unit(user=self.user)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        availability = Availability.objects.create(
            rental_unit=rental_unit,
            instant_booking=True,
            min_stay=2
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 3)
        }
        
        result = self.client.post(RESERVATION_REQUEST_URL, payload)
        
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
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        availability = Availability.objects.create(
            rental_unit=rental_unit,
            instant_booking=True,
            max_stay=20
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 30),
        }
        
        result = self.client.post(RESERVATION_REQUEST_URL, payload)
        
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
            instant_booking=True,
            min_notice=5
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 6, 11),
            'check_out': date(2023, 6, 15),
        }
        
        result = self.client.post(RESERVATION_REQUEST_URL, payload)

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
        
        result = self.client.post(RESERVATION_REQUEST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        
    def test_create_instant_booking_reservation(self):
        """test creating a reservation for a rental unit with instant booking=on"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(
            rental_unit=rental_unit,
            instant_booking=True
        )
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 24),
            'check_out': date(2023, 8, 30)
        }
        result = self.client.post(RESERVATION_REQUEST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Reservation.objects.filter(
            rental_unit=payload['rental_unit'], 
            user=payload['user'],
            check_in=payload['check_in'],
            check_out=payload['check_out']
        ).exists())
        self.assertTrue(CalendarEvent.objects.filter(
            rental_unit=payload['rental_unit'], 
            reason='Reservation',
            start_date=payload['check_in'],
            end_date=payload['check_out']
        ).exists())

    def test_get_nightly_subtotal(self):
        """test getting the nightly subtotal for a reservation"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit, instant_booking=True)
        np = Decimal(100)
        ci = date(2023, 9, 15)
        co = date(2023, 9, 21)
        pricing = Pricing.objects.create(
            rental_unit=rental_unit, 
            night_price=np
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': ci,
            'check_out': co
        }
        result = self.client.post(RESERVATION_REQUEST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        
        reservation = Reservation.objects.filter(
            check_in=payload['check_in'],
            check_out=payload['check_out']
        )[0]
        
        delta = co - ci
        nights = delta.days
        subtotal = nights * np
        self.assertEqual(reservation.subtotal, subtotal)
        
    def test_get_total_days(self):
        """test getting the nightly subtotal for a reservation"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit, instant_booking=True)
        np = Decimal(100)
        ci = date(2023, 9, 15)
        co = date(2023, 9, 21)
        pricing = Pricing.objects.create(
            rental_unit=rental_unit, 
            night_price=np
        )
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': ci,
            'check_out': co
        }
        result = self.client.post(RESERVATION_REQUEST_URL, payload)
        
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        
        reservation = Reservation.objects.filter(
            check_in=payload['check_in'],
            check_out=payload['check_out']
        )[0]
        
        delta = co - ci
        nights = delta.days
        self.assertEqual(reservation.nights, nights)
        
        
class AdminReservationRequestApiTests(TestCase):
    """tests for administrative users"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='super@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_patch_reservation(self):
        """test updating a reservation that has not been confirmed"""
        rental_unit = create_rental_unit(user=self.user)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        availability = Availability.objects.create(rental_unit=rental_unit)
       
        post_payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 6)
        }
        post_result = self.client.post(RESERVATION_REQUEST_URL, post_payload)
        self.assertEqual(post_result.status_code, status.HTTP_201_CREATED)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=post_payload['rental_unit'], 
            user=post_payload['user'],
            check_in=post_payload['check_in'],
            check_out=post_payload['check_out']
        ).exists())
        
        new_check_out = date(2023, 9, 7)
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 9, 1),
            'check_out': new_check_out
        }
        
        reservation_request = ReservationRequest.objects.filter(
            rental_unit=post_payload['rental_unit'], 
            user=post_payload['user'],
            check_in=post_payload['check_in'],
            check_out=post_payload['check_out']
        )[0]
        
        url = detail_url(reservation_request.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        reservation_request.refresh_from_db()
        self.assertEqual(reservation_request.check_out, payload['check_out'])
        
    def test_error_patch_confirmed_reservation(self):
        """test updating a reservation that has been confirmed"""
        rental_unit = create_rental_unit(user=self.user)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        availability = Availability.objects.create(rental_unit=rental_unit, instant_booking=True)
       
        post_payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 6)
        }
        post_result = self.client.post(RESERVATION_REQUEST_URL, post_payload)
        self.assertEqual(post_result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Reservation.objects.filter(
            rental_unit=post_payload['rental_unit'], 
            user=post_payload['user'],
            check_in=post_payload['check_in'],
            check_out=post_payload['check_out']
        ).exists())
        
        new_check_out = date(2023, 9, 7)
        
        payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 9, 1),
            'check_out': new_check_out
        }
        
        reservation_request = ReservationRequest.objects.filter(
            rental_unit=post_payload['rental_unit'], 
            user=post_payload['user'],
            check_in=post_payload['check_in'],
            check_out=post_payload['check_out']
        )[0]
        
        url = detail_url(reservation_request.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        reservation_request.refresh_from_db()
        self.assertEqual(reservation_request.check_out, post_payload['check_out'])
        
    def test_confirm_reservation(self):
        """test updating a reservation that has not been confirmed"""
        rental_unit = create_rental_unit(user=self.user)
        pricing = Pricing.objects.create(rental_unit=rental_unit)
        availability = Availability.objects.create(rental_unit=rental_unit)
       
        post_payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 6)
        }
        post_result = self.client.post(RESERVATION_REQUEST_URL, post_payload)
        
        self.assertEqual(post_result.status_code, status.HTTP_201_CREATED)
        self.assertFalse(Reservation.objects.filter(
            rental_unit=post_payload['rental_unit'], 
            user=post_payload['user'],
            check_in=post_payload['check_in'],
            check_out=post_payload['check_out']
        ).exists())
        
        patch_payload = {
            'rental_unit': rental_unit.id,
            'user': self.user.id,
            'check_in': date(2023, 8, 2),
            'check_out': date(2023, 8, 6),
            'status': True
        }
        
        reservation_request = ReservationRequest.objects.filter(
            rental_unit=post_payload['rental_unit'], 
            user=post_payload['user'],
            check_in=post_payload['check_in'],
            check_out=post_payload['check_out']
        )[0]
        
        url = detail_url(reservation_request.id)
        result = self.client.patch(url, patch_payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        reservation_request.refresh_from_db()
        
        self.assertTrue(Reservation.objects.filter(
            reservation_request=reservation_request
        ).exists())
        
        
    def test_delete_reservation(self):
        """test admin deleting a reservation"""
        rental_unit = create_rental_unit(user=self.user)
        reservation_request = create_reservation_request(user_id=self.user, rental_unit_id=rental_unit)
        
        url = detail_url(reservation_request.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ReservationRequest.objects.filter(id=reservation_request.id).exists())