"""
tests for availability API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import RentalUnit, Availability

from rental_unit.serializers import (
    AvailabilitySerializer,
    AvailabilityDetailSerializer
)


AVAILABILITY_URL = reverse('rental_unit:availability-list')

## HELPER FUNCTIONS
def detail_url(availability_id):
    """create and return a detailed availability URL"""
    return reverse('rental_unit:availability-detail', args=[availability_id])

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
