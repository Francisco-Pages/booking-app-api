"""
views for the rental unit api
"""
from rest_framework import viewsets
from rest_framework import serializers as drf_serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from core.models import RentalUnit, Amenities
from rental_unit import serializers


class RentalUnitViewSet(viewsets.ModelViewSet):
    """view for manage rental unit APIs"""
    serializer_class = serializers.RentalUnitDetailSerializer
    queryset = RentalUnit.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """retrieve rental units for authenticated users"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.RentalUnitSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """create a new rental unit"""
        user = self.request.user
        
        if user.is_staff == False:
            raise drf_serializers.ValidationError('Not authorized to create listings')
        else:
            serializer.save(user=user)
            
    def perform_update(self, serializer):
        user = self.request.user
        
        if user.is_staff == False:
            raise drf_serializers.ValidationError('Not authorized to create listings')
        else:
            serializer.save(user=user)
    
    def perform_destroy(self, instance):
        user = self.request.user
        
        if user.is_staff == False:
            raise drf_serializers.ValidationError('Not authorized to create listings')
        else:
            instance.delete()
            
class AmenitiesViewSet(viewsets.ModelViewSet):
    """view for manage the amenities list for the rental unit APIs"""
    serializer_class = serializers.AmenitiesDetailSerializer
    queryset = Amenities.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """retrieve amenities list for authenticated users"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.AmenitiesSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """create a new amenities list"""
        user = self.request.user
        
        if user.is_staff == False:
            raise drf_serializers.ValidationError('Not authorized to create a list of amenities')
        else:
            serializer.save(user=user)