"""
serializers for rental unit API
"""
from django.conf import settings

from rest_framework import serializers
from datetime import datetime, timedelta, date

import stripe


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
    Reservation,
    CancellationRequest,
    ChangeRequest,
    Photo,
    Payment
)

from rest_framework import serializers as drf_serializers


class PaymentSerializer(serializers.ModelSerializer):
    """serializer for rental unit"""
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id']
        
    def create(self, validated_data):
        payment = Payment.objects.create(**validated_data)
        
        stripe.api_key = settings.STRIPE_SECRET_KEY

        payment_intent = stripe.PaymentIntent.create(
            amount=int(payment.amount), 
            currency=payment.currency, 
            payment_method_types=['card'],
            receipt_email=payment.customer.email
        )
        
        
        return validated_data
    
class PaymentDetailSerializer(PaymentSerializer):
    """Serializer for payment detail view"""
    
    class Meta(PaymentSerializer.Meta):
        fields = PaymentSerializer.Meta.fields 