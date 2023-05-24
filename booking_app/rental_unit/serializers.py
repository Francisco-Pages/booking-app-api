"""
serializers for rental unit API
"""
from rest_framework import serializers

from core.models import RentalUnit, Amenities


class RentalUnitSerializer(serializers.ModelSerializer):
    """serializer for rental unit"""
    
    class Meta:
        model = RentalUnit
        fields = [
            'id', 
            'title', 
            'description', 
            'link', 
            'languages',
            'status', 
            'images', 
            'unit_type', 
            'max_guests',
            'amenities',
            'location', 
        ]
        read_only_fields = ['id']
        
class RentalUnitDetailSerializer(RentalUnitSerializer):
    """Serializer for rental unit detail view"""
    
    class Meta(RentalUnitSerializer.Meta):
        fields = RentalUnitSerializer.Meta.fields 
        
class AmenitiesSerializer(serializers.ModelSerializer):
    """serializer for an amenities list"""
    
    class Meta:
        model = Amenities
        fields = '__all__'
        read_only_fields = ['id']
        
class AmenitiesDetailSerializer(AmenitiesSerializer):
    """Serializer for amenities list detail view"""
    
    class Meta(AmenitiesSerializer.Meta):
        fields = AmenitiesSerializer.Meta.fields 