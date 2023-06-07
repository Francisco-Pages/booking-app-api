"""
serializers for rental unit API
"""
from rest_framework import serializers

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


class RentalUnitSerializer(serializers.ModelSerializer):
    """serializer for rental unit"""
    class Meta:
        model = RentalUnit
        fields = '__all__'
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
        
        
class AvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for Availability"""
    
    class Meta:
        model = Availability
        fields = '__all__'
        # read_only_fields = ['rental_unit']


class AvailabilityDetailSerializer(AvailabilitySerializer):
    """Serializer for Availability detail view"""
    
    class Meta(AvailabilitySerializer.Meta):
        fields = AvailabilitySerializer.Meta.fields 
        
        
class CalendarEventSerializer(serializers.ModelSerializer):
    """Serializer for CalendarEvent"""
    
    class Meta:
        model = CalendarEvent
        fields = '__all__'
        read_only_fields = ['creation_date', 'rental_unit','id']


class CalendarEventDetailSerializer(CalendarEventSerializer):
    """Serializer for CalendarEvent detail view"""
    
    class Meta(CalendarEventSerializer.Meta):
        fields = CalendarEventSerializer.Meta.fields 
        
        
class RulebookSerializer(serializers.ModelSerializer):
    """Serializer for Rulebook"""
    
    class Meta:
        model = Rulebook
        fields = '__all__'
        # read_only_fields = ['rental_unit']


class RulebookDetailSerializer(RulebookSerializer):
    """Serializer for rulebook detail view"""
    
    class Meta(RulebookSerializer.Meta):
        fields = RulebookSerializer.Meta.fields 
        
         
class GuidebookSerializer(serializers.ModelSerializer):
    """Serializer for Guidebook"""
    
    class Meta:
        model = Guidebook
        fields = '__all__'
        # read_only_fields = ['rental_unit']
    
    
class GuidebookDetailSerializer(GuidebookSerializer):
    """Serializer for guidebook detail view"""
    
    class Meta(GuidebookSerializer.Meta):
        fields = GuidebookSerializer.Meta.fields 
        

class PlaceSerializer(serializers.ModelSerializer):
    """Serializer for a place"""

    class Meta:
        model = Place
        fields = '__all__'
        read_only_fields = ['id']


class PlaceDetailSerializer(PlaceSerializer):
    """Serializer for Place detail view"""
    
    class Meta(PlaceSerializer.Meta):
        fields = PlaceSerializer.Meta.fields        
        
        