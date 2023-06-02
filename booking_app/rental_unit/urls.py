"""
URL mappings for rental unit API
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from rental_unit import views


router = DefaultRouter()
router.register('rental_units', views.RentalUnitViewSet)
router.register('amenities_lists', views.AmenitiesListViewSet)
router.register('locations', views.LocationViewSet)
router.register('rooms', views.RoomViewSet)
router.register('pricings', views.PricingViewSet)
router.register('fees', views.FeeViewSet)
router.register('availabilitys', views.AvailabilityViewSet)
router.register('calendar_events', views.CalendarEventViewSet)




app_name = 'rental_unit'

urlpatterns = [
    path('', include(router.urls)),
]
