"""
views for the rental unit api
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import RentalUnit
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
        """create a new recipe"""
        serializer.save(user=self.request.user)
        