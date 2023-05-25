"""
views for the rental unit api
"""
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework import serializers as drf_serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from core.models import RentalUnit
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
    permission_classes = [IsAuthenticated]
    
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
            
# class AmenitiesViewSet(viewsets.ModelViewSet):
#     """view for manage the amenities list for the rental unit APIs"""
#     serializer_class = serializers.AmenitiesDetailSerializer
#     queryset = Amenities.objects.all()
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
    
#     def get_queryset(self):
#         """retrieve amenities list for authenticated users"""
#         return self.queryset.all().order_by('-id')
    
#     def get_serializer_class(self):
#         """returns serializer class for request"""
#         if self.action == 'list':
#             return serializers.AmenitiesSerializer
#         return self.serializer_class
    
    # def perform_create(self, serializer):
    #     """create a new amenities list"""
    #     user = self.request.user
    #     rental_unit_of_user = RentalUnit.objects.filter(user=user)
    #     if user.is_staff == False:
    #         raise drf_serializers.ValidationError('Not authorized to create a list of amenities')
    #     if rental_unit_of_user.rental_unit_id not in RentalUnit.objects.filter:
    #         serializer.save(user=user)