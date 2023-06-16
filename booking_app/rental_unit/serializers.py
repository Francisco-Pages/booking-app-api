"""
serializers for rental unit API
"""
from rest_framework import serializers
from datetime import datetime, timedelta, date

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
    ReservationRequest,
    Reservation
)

from rest_framework import serializers as drf_serializers


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
        read_only_fields = ['id', 'creation_date']
        
    def validate(self, data):
        now = datetime.now().date()
        
        """FOR WHEN YOU FIGURE OUT HOW TO REMOVE DATA DEPENDENCIES!!!!!"""
        instance_id = False
        if 'PATCH' in str(self.context):
            mystr = str(self.context['request'])
            start_of = mystr.index('events/') + 7
            instance_id = mystr[start_of:-3]
            calendar_event = CalendarEvent.objects.get(id=instance_id)
            if 'rental_unit' not in data:
                data['rental_unit'] = calendar_event.rental_unit
            if 'start_date' not in data:
                data['start_date'] = calendar_event.start_date
            if 'end_date' not in data:
                data['end_date'] = calendar_event.end_date
        
        """check that essential information is provided"""
        if 'rental_unit' not in data:
            raise drf_serializers.ValidationError('Error: please enter a rental unit')
        
        
        if 'start_date' not in data or 'end_date' not in data:
            raise drf_serializers.ValidationError('Error: please enter start and end dates')
        
        """check that start date in not in the past"""
        if data['start_date'] <= now:
            raise drf_serializers.ValidationError("Error: let go of the past. it is gone. forget it. she doesn't want you.")
        
        """check that start date is not on or after end date"""
        if data['start_date'] >= data['end_date']:
            raise drf_serializers.ValidationError('Start date cannot be on or before end date, please choose another date.')
        if 'reason' not in data:
            data['reason'] = 'Blocked'
        
        """check that the chosen dates are available"""
        calendar_event_list = CalendarEvent.objects.filter(rental_unit=data['rental_unit'])
        if instance_id:
            calendar_event_list = CalendarEvent.objects.filter(rental_unit=data['rental_unit']).exclude(id=instance_id)
        
        availability = Availability.objects.get(rental_unit=data['rental_unit'])
        prep = timedelta(days=availability.prep_time)
        
        start_date = data['start_date']
        end_date = data['end_date']
        
        for event in calendar_event_list:
            if start_date < event.end_date + prep and start_date >= event.start_date or \
                end_date <= event.end_date and end_date > event.start_date + prep or \
                start_date <= event.start_date and end_date >= event.end_date:

                raise drf_serializers.ValidationError(f'Sorry, the dates you have chosen are not available, there is another reservation from {event.start_date} to {event.end_date}')
        
        return data

    def update(self, instance, validated_data):    
        instance.rental_unit = validated_data.get('rental_unit', instance.rental_unit)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.save()
        
        return instance

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


class ReservationRequestSerializer(serializers.ModelSerializer):
    """Serializer for a ReservationRequest"""

    class Meta:
        model = ReservationRequest
        fields = '__all__'
        read_only_fields = ['id']
        
    def validate(self, data):
        """validations for reservation requests"""
        now = datetime.now().date()

        """check that check in and check out dates are given"""
        if 'check_in' not in data or 'check_out' not in data:
            raise drf_serializers.ValidationError('Error: please enter check in and check out dates')
        if 'rental_unit' not in data:
            raise drf_serializers.ValidationError('Error: please enter a rental unit')
        
        if data['check_in'] <= now:
            raise drf_serializers.ValidationError("Error: let go of the past. it is gone. forget it. she doesn't want you.")
        
        """check that check in date is not on or before check out date"""
        if data['check_in'] >= data['check_out']:
            raise drf_serializers.ValidationError('Check in date cannot be on or before check out date, please choose another date.')
        
        """check that the chosen dates are available"""
        reservaton_list = Reservation.objects.filter(rental_unit=data['rental_unit'])
        availability = Availability.objects.get(rental_unit=data['rental_unit'])
        prep = timedelta(days=availability.prep_time)
        
        check_in = data['check_in']
        check_out = data['check_out']
        
        """check that a new reservation does not overlap with an existing reservation"""
        for reservation in reservaton_list:
            if check_in < reservation.check_out + prep and check_in >= reservation.check_in or \
                check_out <= reservation.check_out and check_out > reservation.check_in + prep or \
                check_in <= reservation.check_in and check_out >= reservation.check_out:
                
                raise drf_serializers.ValidationError(f'Sorry, the dates you have chosen are not available, there is another reservation from {reservation.check_in} to {reservation.check_out}')
        
        """check that the the dates chosen for a reservation are not blocked"""
        calendar_event_list = CalendarEvent.objects.filter(rental_unit=data['rental_unit'])
        for event in calendar_event_list:
            if check_in < event.end_date + prep and check_in >= event.start_date or \
                check_out <= event.end_date and check_out > event.start_date + prep or \
                check_in <= event.start_date and check_out >= event.end_date:

                raise drf_serializers.ValidationError(f'Sorry, the dates you have chosen are not available, there is another reservation from {event.start_date} to {event.end_date}')

        """check that the reservation length is within the boundaries set by the rental unit owner"""
        availability = Availability.objects.get(rental_unit=data['rental_unit'])
        delta = check_out - check_in
        
        if delta.days < availability.min_stay:
            raise drf_serializers.ValidationError(f'Reservation must be longer than {availability.min_stay}')
        if delta.days > availability.max_stay:
            raise drf_serializers.ValidationError(f'Reservation must be shorter than {availability.max_stay}') 
        
        """check that a reservation is made within the notice boundaries set by the rental unit owner"""
        now = datetime.now().date()
        testing_now = date(2023, 6, 7)
        delta = check_in - testing_now
        
        if delta.days < availability.min_notice:
            raise drf_serializers.ValidationError(f'Reservation must be made at least {availability.min_notice} days before check in date.')
        if delta.days > availability.max_notice:
            raise drf_serializers.ValidationError(f'Reservation must be made at most {availability.max_notice} days before check in date.')
        
        return data
    
    def create(self, validated_data):
        """create a return reservation request"""
        reservation_request = ReservationRequest.objects.create(**validated_data)
        availability = Availability.objects.get(rental_unit=reservation_request.rental_unit)
        pricing = Pricing.objects.get(rental_unit=reservation_request.rental_unit)
        
        night_price = pricing.night_price
        stay_length = (reservation_request.check_out - reservation_request.check_in).days
        subtotal = night_price * stay_length
        total = subtotal + (subtotal * pricing.tax)
        if availability.instant_booking == True:
            reservation = Reservation.objects.create(
                rental_unit=reservation_request.rental_unit,
                reservation_request=reservation_request,
                user=reservation_request.user,
                check_in=reservation_request.check_in,
                check_out=reservation_request.check_out,
                night_price=pricing.night_price,
                subtotal=subtotal,
                taxes=pricing.tax,
                total=total
            )
            reservation.save()
            
            calendar_event = CalendarEvent.objects.create(
                rental_unit=reservation_request.rental_unit,
                reason='Reservation',
                start_date=reservation.check_in,
                end_date=reservation.check_out,
            )
            calendar_event.save()
        
        return reservation_request
        
    def update(self, instance, validated_data):
        if Reservation.objects.filter(reservation_request=instance.id).exists():
            raise drf_serializers.ValidationError("Error: cannot edit a reservation request for a confirmed reservation")
        
        """create data to populate reservation fields after admin confirms reservation request"""
        pricing = Pricing.objects.get(rental_unit=instance.rental_unit)
        night_price = pricing.night_price
        stay_length = (instance.check_out - instance.check_in).days
        subtotal = night_price * stay_length
        total = subtotal + (subtotal * pricing.tax)
        
        """status == True if admin confirms reservation request, if not, save request without creating reservation"""
        if 'status' in validated_data and validated_data['status'] == True:
            instance.status = validated_data.get('status', instance.status)
        instance.rental_unit = validated_data.get('rental_unit', instance.rental_unit)
        instance.user = validated_data.get('user', instance.user)
        instance.check_in = validated_data.get('check_in', instance.check_in)
        instance.check_out = validated_data.get('check_out', instance.check_out)
        instance.save()
        
        """create reservation and save to calendar if status == True"""
        if instance.status == True:
            calendar_event = CalendarEvent.objects.create(
                rental_unit=instance.rental_unit,
                reason='Reservation',
                start_date=instance.check_in,
                end_date=instance.check_out,
            )
            calendar_event.save()
            
            reservation = Reservation.objects.create(
                rental_unit=instance.rental_unit,
                reservation_request=instance,
                user=instance.user,
                check_in=instance.check_in,
                check_out=instance.check_out,
                night_price=pricing.night_price,
                subtotal=subtotal,
                taxes=pricing.tax,
                total=total
            )
            reservation.save()
    
        return instance
        
        
class ReservationRequestDetailSerializer(ReservationRequestSerializer):
    """Serializer for Reservation detail view"""
    
    class Meta(ReservationRequestSerializer.Meta):
        fields = ReservationRequestSerializer.Meta.fields
        
    
class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for a Reservation"""

    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['id']
        
        
class ReservationDetailSerializer(ReservationSerializer):
    """Serializer for Reservation detail view"""
    
    class Meta(ReservationSerializer.Meta):
        fields = ReservationSerializer.Meta.fields