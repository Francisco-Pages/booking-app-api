"""
serializers for rental unit API
"""
from rest_framework import serializers
from datetime import datetime, timedelta

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
    Place,
    Reservation
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
        
        
class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for a Reservation"""

    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['id']
        
    def validate(self, data):
        """check that check in date is not on or before check out date"""
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError('Check in date cannot be on or before check out date, please choose another date.')
        
        """check that a new reservation does not overlap with an existing reservation"""
        reservaton_list = Reservation.objects.filter(rental_unit=data['rental_unit'])
        availability = Availability.objects.get(rental_unit=data['rental_unit'])
        prep = timedelta(days=availability.prep_time)
        
        for reservation in reservaton_list:
            if data['check_in'] < reservation.check_out + prep and data['check_in'] >= reservation.check_in or \
                data['check_out'] <= reservation.check_out and data['check_out'] > reservation.check_in + prep or \
                data['check_in'] <= reservation.check_in and data['check_out'] >= reservation.check_out:
                
                raise serializers.ValidationError(f'Sorry, the dates you have chosen are not available, there is another reservation from {reservation.check_in} to {reservation.check_out}')
        
        """check that the the dates chosen for a reservation are not blocked"""
        calendar_event_list = CalendarEvent.objects.filter(rental_unit=data['rental_unit'])
        for event in calendar_event_list:
            if data['check_in'] < event.end_date + prep and data['check_in'] >= event.start_date or \
                data['check_out'] <= event.end_date and data['check_out'] > event.start_date + prep or \
                data['check_in'] <= event.start_date and data['check_out'] >= event.end_date:

                raise serializers.ValidationError(f'Sorry, the dates you have chosen are not available, there is another reservation from {event.start_date} to {event.end_date}')

        """check that the reservation length is within the boundaries set by the rental unit owner"""
        availability = Availability.objects.get(rental_unit=data['rental_unit'])
        delta = data['check_out'] - data['check_in']
        if delta.days < availability.min_stay:
            raise serializers.ValidationError(f'Reservation must be longer than {availability.min_stay}')
        if delta.days > availability.max_stay:
            raise serializers.ValidationError(f'Reservation must be shorter than {availability.max_stay}') 
        
        """check that a reservation is made within the notice boundaries set by the rental unit owner"""
        delta = data['check_in'] - datetime.now().date()
        if delta.days < availability.min_notice:
            raise serializers.ValidationError(f'Reservation must be made at least {availability.min_notice} days before check in date.')
        if delta.days > availability.max_notice:
            raise serializers.ValidationError(f'Reservation must be made at most {availability.max_notice} days before check in date.')
        
        return data

class ReservationDetailSerializer(ReservationSerializer):
    """Serializer for Reservation detail view"""
    
    class Meta(ReservationSerializer.Meta):
        fields = ReservationSerializer.Meta.fields        