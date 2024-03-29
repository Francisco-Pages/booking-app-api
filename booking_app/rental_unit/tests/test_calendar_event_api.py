"""
tests for calendar_event API
"""
from decimal import Decimal
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, CalendarEvent, Availability

from rental_unit.serializers import (
    CalendarEventSerializer,
    CalendarEventDetailSerializer
)


CALENDAR_EVENT_URL = reverse('rental_unit:calendarevent-list')

def detail_url(calendar_event_id):
    """create and return a detailed calendar_event URL"""
    return reverse('rental_unit:calendarevent-detail', args=[calendar_event_id])

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
class PublicCalendarEventApiTests(TestCase):
    """tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_get_calendar_event_by_non_auth(self):
        """test that unauthenticated requests can read CalendarEvents"""
        result = self.client.get(CALENDAR_EVENT_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        
    def test_get_calendar_event_detail_by_non_auth(self):
        """test that an unauthenticated request can read a detailed calendar_event"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        rental_unit = create_rental_unit(user=user)
        calendar_event = CalendarEvent.objects.create(rental_unit=rental_unit, reason='Reserved')
        
        url = detail_url(calendar_event.id)
        result = self.client.get(url)
        
        self.assertTrue(result.status_code, status.HTTP_200_OK)
        serializer = CalendarEventDetailSerializer(calendar_event)
        self.assertEqual(result.data, serializer.data)
        

class PrivateCalendarEventApiTests(TestCase):
    """test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com', 
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_all_calendar_events_list(self):
        """test retrieving a list of CalendarEvents"""
        rental_unit = create_rental_unit(user=self.user)
        rental_unit_two = create_rental_unit(user=self.user)
        
        CalendarEvent.objects.create(rental_unit=rental_unit, reason='Reserved')
        CalendarEvent.objects.create(rental_unit=rental_unit_two, reason='Reserved')
        
        result = self.client.get(CALENDAR_EVENT_URL)
        
        calendar_events = CalendarEvent.objects.all().order_by('-start_date')
        serializer = CalendarEventSerializer(calendar_events, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        
    def test_get_calendar_event_detail(self):
        """test get rental unit detail"""
        rental_unit = create_rental_unit(user=self.user)
        calendar_event = CalendarEvent.objects.create(rental_unit=rental_unit, reason='Reserved')
        
        url = detail_url(calendar_event.id)
        result = self.client.get(url)

        serializer = CalendarEventDetailSerializer(calendar_event)
        self.assertEqual(result.data, serializer.data)
        
    def test_error_create_calendar_event(self):
        """test error creating a CalendarEvent by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        
        payload = {
            'rental_unit': rental_unit.id,
            'reason': 'Reservation',
            'start_date': date(2023, 6, 28),
            'end_date': date(2023, 6, 30)
        }
        
        result = self.client.post(CALENDAR_EVENT_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(CalendarEvent.objects.filter(
            rental_unit=payload['rental_unit'], 
            start_date=payload['start_date'],
            end_date=payload['end_date']
        ).exists())
        
    def test_error_partial_update(self):
        """test error patch of a calendar_event by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_reason = 'Blocked'
        
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason=original_reason,
        )

        payload = {
            'rental_unit': rental_unit.id,
            'reason': 'Reservation',
        }
        
        url = detail_url(calendar_event.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        calendar_event.refresh_from_db()
        self.assertEqual(calendar_event.reason, original_reason)
        
    def test_error_full_update(self):
        """test error put of calendar_event by non admin"""
        rental_unit = create_rental_unit(user=self.user)
        original_reason = 'Blocked'
        original_start = date(2023, 6, 28)
        original_end = date(2023, 7, 4)
        
        
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason=original_reason,
            start_date=original_start,
            end_date=original_end,
        )

        payload = {
            'id': calendar_event.id,
            'reason': 'Reservation',
            'start_date': date(2023,6,20),
            'end_date': date(2023,6,27),
        }
        
        url = detail_url(calendar_event.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        calendar_event.refresh_from_db()

        self.assertEqual(CalendarEvent.objects.get(id=calendar_event.id).start_date, original_start)
        
    def test_error_delete_calendar_event(self):
        """test error when deleting a CalendarEvent by a non admin"""
        rental_unit = create_rental_unit(user=self.user)
        calendar_event = CalendarEvent.objects.create(rental_unit=rental_unit, reason='Reserved')
        
        url = detail_url(calendar_event.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CalendarEvent.objects.filter(id=calendar_event.id).exists())
        
        
class AdminCalendarEventApiTests(TestCase):
    """test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(
            email='testadmin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_calendar_event(self):
        """test creating a CalendarEvent by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        payload = {
            'rental_unit': rental_unit.id,
            'reason': 'Reservation',
            'start_date': date(2023, 6, 28),
            'end_date': date(2023, 6, 30),
        }
        result = self.client.post(CALENDAR_EVENT_URL, payload)

        self.assertTrue(CalendarEvent.objects.filter(
            rental_unit=payload['rental_unit'], 
            start_date=payload['start_date'],
            end_date=payload['end_date']
        ).exists())
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_partial_update(self):
        """test patch of a calendar_event by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        original_reason = 'Blocked'
        original_start = date(2023, 6, 28)
        original_end = date(2023, 7, 4)
        
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason=original_reason,
            start_date=original_start,
            end_date=original_end
        )

        payload = {
            'rental_unit': rental_unit.id,
            'reason': 'Reservation',
            'start_date': date(2023, 6, 28),
            'end_date': date(2023, 7, 4)
        }
        
        url = detail_url(calendar_event.id)
        result = self.client.patch(url, payload)
        print(result.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        calendar_event.refresh_from_db()
        self.assertEqual(calendar_event.reason, payload['reason'])
        self.assertEqual(calendar_event.start_date, original_start)
        
    def test_full_update(self):
        """test put of calendar_event"""
        rental_unit = create_rental_unit(user=self.user)
        availability = Availability.objects.create(rental_unit=rental_unit)
        original_reason = 'Blocked'
        original_start = date(2023, 6, 28)
        original_end = date(2023, 7, 4)
        
        
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason=original_reason,
            start_date=original_start,
            end_date=original_end,
        )

        payload = {
            'rental_unit': rental_unit.id,
            'reason': 'Reservation',
            'start_date': date(2023,6,20),
            'end_date': date(2023,6,27),
        }
        
        url = detail_url(calendar_event.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        calendar_event.refresh_from_db()
        
        for k, v in payload.items():
            if k == 'rental_unit' or k == 'creation_date':
                continue
            self.assertEqual(getattr(calendar_event, k), v)
        
    def test_delete_calendar_event(self):
        """test deleting a CalendarEvent is successful"""
        rental_unit = create_rental_unit(user=self.user)
        calendar_event = CalendarEvent.objects.create(rental_unit=rental_unit, reason='Reserved')
        
        url = detail_url(calendar_event.id)
        result = self.client.delete(url)
        
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CalendarEvent.objects.filter(id=calendar_event.id).exists())