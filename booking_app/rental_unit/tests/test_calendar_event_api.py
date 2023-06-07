"""
tests for calendar_event API
"""
from decimal import Decimal
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, CalendarEvent

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
        
        calendar_events = CalendarEvent.objects.all().order_by('-rental_unit')
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
            'start_date': "2023-06-28T12:38:30.756209Z",
            'notes': f'reservation for unit #{rental_unit.id}'
        }
        
        result = self.client.post(CALENDAR_EVENT_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(CalendarEvent.objects.filter(notes=payload['notes']).exists())
        
    def test_error_partial_update(self):
        """test error patch of a calendar_event by a non administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_reason = 'Blocked'
        original_notes = 'sample notes'
        
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason=original_reason,
            notes=original_notes, 
        )

        payload = {
            'rental_unit': rental_unit.id,
            'reason': 'Reservation',
            'notes': f'reservation updated for unit #{rental_unit.id}'
        }
        
        url = detail_url(calendar_event.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        calendar_event.refresh_from_db()
        self.assertEqual(calendar_event.reason, original_reason)
        self.assertEqual(calendar_event.notes, original_notes)
        
    def test_error_full_update(self):
        """test error put of calendar_event by non admin"""
        rental_unit = create_rental_unit(user=self.user)
        original_reason = 'Blocked'
        original_start = '2023-06-28T12:38:30.756209Z'
        original_end = '2023-07-4T12:38:30.756209Z'
        original_notes = f"reservation for rental unit #{rental_unit.id}"
        
        
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason=original_reason,
            start_date=original_start,
            end_date=original_end,
            notes=original_notes, 
        )

        payload = {
            'id': calendar_event.id,
            'reason': 'Reservation',
            'start_date': datetime(2023,6,20,12,38,30, tzinfo=timezone.utc),
            'end_date': datetime(2023,6,27,12,38,30, tzinfo=timezone.utc),
            'notes': f'reservation updated for unit #{rental_unit.id}'
        }
        
        url = detail_url(calendar_event.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        calendar_event.refresh_from_db()

        self.assertEqual(getattr(calendar_event, 'notes'), original_notes)
        
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
        
        payload = {
            'rental_unit': rental_unit.id,
            'reason': 'Reservation',
            'start_date': "2023-06-28T12:38:30.756209Z",
            'notes': f'reservation for unit #{rental_unit.id}'
        }
        result = self.client.post(CALENDAR_EVENT_URL, payload)

        self.assertTrue(CalendarEvent.objects.filter(notes=payload['notes']).exists())
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    # def test_error_create_double_calendar_event(self):
    #     """test that there can only be one type of calendar_event for one rental unit"""
    #     rental_unit = create_rental_unit(user=self.user)
    #     calendar_event = CalendarEvent.objects.create(
    #         rental_unit=rental_unit,
    #         name='Pet',
    #         price=Decimal('50.51')
    #     )
        
    #     payload = {
    #         'rental_unit': rental_unit.id,
    #         'name': 'Pet',
    #         'price': Decimal('50.50')
    #     }
    #     result = self.client.post(CALENDAR_EVENT_URL, payload)
        
    #     self.assertEqual(calendar_event.price, Decimal('50.51'))
    #     self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertFalse(CalendarEvent.objects.filter(rental_unit=payload['rental_unit'], name=payload['name'], price=payload['price']).exists())
           
    def test_partial_update(self):
        """test patch of a calendar_event by an administrator"""
        rental_unit = create_rental_unit(user=self.user)
        original_reason = 'Blocked'
        original_notes = 'sample notes'
        
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason=original_reason,
            notes=original_notes, 
        )

        payload = {
            'rental_unit': rental_unit.id,
            'reason': 'Reservation',
            'notes': f'reservation updated for unit #{rental_unit.id}'
        }
        
        url = detail_url(calendar_event.id)
        result = self.client.patch(url, payload)
        
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        calendar_event.refresh_from_db()
        self.assertEqual(calendar_event.reason, payload['reason'])
        self.assertEqual(calendar_event.notes, payload['notes'])
        
    def test_full_update(self):
        """test put of calendar_event"""
        rental_unit = create_rental_unit(user=self.user)
        original_reason = 'Blocked'
        original_start = '2023-06-28T12:38:30.756209Z'
        original_end = '2023-07-4T12:38:30.756209Z'
        original_notes = f"reservation for rental unit #{rental_unit.id}"
        
        
        calendar_event = CalendarEvent.objects.create(
            rental_unit=rental_unit,
            reason=original_reason,
            start_date=original_start,
            end_date=original_end,
            notes=original_notes, 
        )

        payload = {
            'id': calendar_event.id,
            'reason': 'Reservation',
            'start_date': datetime(2023,6,20,12,38,30, tzinfo=timezone.utc),
            'end_date': datetime(2023,6,27,12,38,30, tzinfo=timezone.utc),
            'notes': f'reservation updated for unit #{rental_unit.id}'
        }
        
        url = detail_url(calendar_event.id)
        
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        calendar_event.refresh_from_db()
        
        for k, v in payload.items():
            if k == 'rental_unit':
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