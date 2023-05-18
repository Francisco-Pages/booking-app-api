"""
serializers for rental unit API
"""
from rest_framework import serializers

from core.models import RentalUnit


class RentalUnitSerializer(serializers.ModelSerializer):
    """serializer for rental unit"""
    
    class Meta:
        model = RentalUnit
        fields = [
            'id', 
            'title', 
            'price', 
            'unit_type', 
            'status', 
            'max_guests', 
            'wifi_name', 
            'wifi_password', 
            'house_rules'
        ]
        read_only_fields = ['id']
        
class RentalUnitDetailSerializer(RentalUnitSerializer):
    """Serializer for rental unit detail view"""
    
    class Meta(RentalUnitSerializer.Meta):
        fields = RentalUnitSerializer.Meta.fields + ['description']