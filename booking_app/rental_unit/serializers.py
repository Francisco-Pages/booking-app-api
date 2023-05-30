"""
serializers for rental unit API
"""
from rest_framework import serializers

from core.models import RentalUnit, AmenitiesList, Location, Room, Pricing, Fee


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
        ]
        read_only_fields = ['id']
        
    
class RentalUnitDetailSerializer(RentalUnitSerializer):
    """Serializer for rental unit detail view"""
    
    class Meta(RentalUnitSerializer.Meta):
        fields = RentalUnitSerializer.Meta.fields 
        
    
class AmenitiesListSerializer(serializers.ModelSerializer):
    """Serializer for amenities list"""
    
    class Meta:
        model = AmenitiesList
        fields = '__all__'
        # read_only_fields = ['rental_unit']


class AmenitiesListDetailSerializer(AmenitiesListSerializer):
    """Serializer for amenities list detail view"""
    
    class Meta(AmenitiesListSerializer.Meta):
        fields = AmenitiesListSerializer.Meta.fields 
        
        
class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location"""
    
    class Meta:
        model = Location
        fields = '__all__'
        # read_only_fields = ['rental_unit']


class LocationDetailSerializer(LocationSerializer):
    """Serializer for amenities list detail view"""
    
    class Meta(LocationSerializer.Meta):
        fields = LocationSerializer.Meta.fields 
        

class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room"""
    
    class Meta:
        model = Room
        fields = '__all__'
        # read_only_fields = ['rental_unit']


class RoomDetailSerializer(RoomSerializer):
    """Serializer for Room detail view"""
    
    class Meta(RoomSerializer.Meta):
        fields = RoomSerializer.Meta.fields 
        

class PricingSerializer(serializers.ModelSerializer):
    """Serializer for Pricing"""
    
    class Meta:
        model = Pricing
        fields = '__all__'
        # read_only_fields = ['rental_unit']


class PricingDetailSerializer(PricingSerializer):
    """Serializer for Room detail view"""
    
    class Meta(PricingSerializer.Meta):
        fields = PricingSerializer.Meta.fields 
        

class FeeSerializer(serializers.ModelSerializer):
    """Serializer for Fee"""
    
    class Meta:
        model = Fee
        fields = '__all__'
        # read_only_fields = ['rental_unit']


class FeeDetailSerializer(FeeSerializer):
    """Serializer for Fee detail view"""
    
    class Meta(FeeSerializer.Meta):
        fields = FeeSerializer.Meta.fields 