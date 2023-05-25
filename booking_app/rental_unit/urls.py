"""
URL mappings for rental unit API
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from rental_unit import views


router = DefaultRouter()
router.register('rental_units', views.RentalUnitViewSet)
# router.register('amenities', views.AmenitiesViewSet)

app_name = 'rental_unit'

urlpatterns = [
    path('', include(router.urls)),
]
