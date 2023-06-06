"""
views for the rental unit api
"""
from django.contrib.auth import get_user_model

from rest_framework import viewsets, mixins
from rest_framework import serializers as drf_serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions, response, status

from core.models import (
    RentalUnit, 
    AmenitiesList, 
    Location, 
    Room, 
    Pricing, 
    Fee, 
    Availability, 
    CalendarEvent,
    Rulebook,
    Guidebook,
    Place
)
from rental_unit import serializers


### HELPER FUNCTIONS ###
def get_rental_units_of_user(user):
    user = get_user_model().objects.get(user=user)
    rental_units_of_user = RentalUnit.objects.filter(user=user)
    
    return [i for i in rental_units_of_user]

class RentalUnitViewSet(viewsets.ModelViewSet):
    """view for manage rental unit APIs"""
    serializer_class = serializers.RentalUnitDetailSerializer
    queryset = RentalUnit.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """retrieve rental units for authenticated users"""
        return self.queryset.all().order_by('-id')
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.RentalUnitSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """create a new rental unit"""
        user = self.request.user
        
        if user.is_staff == False:
            raise drf_serializers.ValidationError(
                'Not authorized to create listings'
            )
        else:
            serializer.save(user=user)
            
    def perform_update(self, serializer):
        user = self.request.user
        
        if user.is_staff == False:
            raise drf_serializers.ValidationError(
                'Not authorized to update listings'
            )
        else:
            serializer.save(user=user)
    
    def perform_destroy(self, instance):
        user = self.request.user
        
        if user.is_staff == False:
            raise drf_serializers.ValidationError(
                'Not authorized to delete listings'
            )
        else:
            instance.delete()

class AmenitiesListViewSet(viewsets.ModelViewSet):
    """view for manage the amenities list for the rental unit APIs"""
    serializer_class = serializers.AmenitiesListDetailSerializer
    queryset = AmenitiesList.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve amenities list for authenticated users"""
        return self.queryset.all().order_by('-rental_unit')
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.AmenitiesListSerializer
        return self.serializer_class

    
class LocationViewSet(viewsets.ModelViewSet):
    """view for manage the location for the rental unit APIs"""
    serializer_class = serializers.LocationDetailSerializer
    queryset = Location.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve locations for authenticated users"""
        return self.queryset.all().order_by('-rental_unit')   
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.LocationSerializer
        return self.serializer_class
    
    
class RoomViewSet(viewsets.ModelViewSet):
    """view for manage the Room for the rental unit APIs"""
    serializer_class = serializers.RoomDetailSerializer
    queryset = Room.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve locations for authenticated users"""
        return self.queryset.all().order_by('-rental_unit')   
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.RoomSerializer
        return self.serializer_class
    
    
class PricingViewSet(viewsets.ModelViewSet):
    """view for manage the Pricing for the rental unit APIs"""
    serializer_class = serializers.PricingDetailSerializer
    queryset = Pricing.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve Pricing for authenticated users"""
        return self.queryset.all().order_by('-rental_unit')   
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.PricingSerializer
        return self.serializer_class    
    
    
class FeeViewSet(viewsets.ModelViewSet):
    """view for manage the Fee for the rental unit APIs"""
    serializer_class = serializers.FeeDetailSerializer
    queryset = Fee.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve Fee for authenticated users"""
        return self.queryset.all().order_by('-rental_unit')   
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.FeeSerializer
        return self.serializer_class
    
    
class AvailabilityViewSet(viewsets.ModelViewSet):
    """view for manage the Availability for the rental unit APIs"""
    serializer_class = serializers.AvailabilityDetailSerializer
    queryset = Availability.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve Availability for authenticated users"""
        return self.queryset.all().order_by('-rental_unit')   
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.AvailabilitySerializer
        return self.serializer_class
    
    
class CalendarEventViewSet(viewsets.ModelViewSet):
    """view for manage the Fee for the rental unit APIs"""
    serializer_class = serializers.CalendarEventDetailSerializer
    queryset = CalendarEvent.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve CalendarEvent for authenticated users"""
        return self.queryset.all().order_by('-rental_unit')   
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.CalendarEventSerializer
        return self.serializer_class
    
    
class RulebookViewSet(viewsets.ModelViewSet):
    """view for manage the Rulebook for the rental unit APIs"""
    serializer_class = serializers.RulebookDetailSerializer
    queryset = Rulebook.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve Rulebook for authenticated users"""
        return self.queryset.all().order_by('-rental_unit')   
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.RulebookSerializer
        return self.serializer_class
    
    
class GuidebookViewSet(viewsets.ModelViewSet):
    """view for manage the Guidebook for the rental unit APIs"""
    serializer_class = serializers.GuidebookDetailSerializer
    queryset = Guidebook.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve Guidebook for authenticated users"""
        return self.queryset.all().order_by('-rental_unit')   
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.GuidebookSerializer
        return self.serializer_class
    
    
class PlaceViewSet(viewsets.ModelViewSet):
    """Manage places in the database"""
    serializer_class = serializers.PlaceSerializer
    queryset = Place.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve places for authenticated users"""
        return self.queryset.all().order_by('-rental_unit') 
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.PlaceSerializer
        return self.serializer_class