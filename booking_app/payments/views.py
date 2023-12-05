from django.shortcuts import render
import stripe
from django.conf import settings


# from rest_framework import status
# from rest_framework.response import Response
from rest_framework.decorators import api_view


"""
views for the rental unit api
"""
from django.contrib.auth import get_user_model

from rest_framework import viewsets, mixins
from rest_framework import serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions, response, status

from core.models import (
    
    Payment
)
from payments import serializers


# stripe.api_key = settings.STRIPE_SECRET_KEY
# # Create your views here.
# @api_view(['POST'])
# def test_payment(request):
#     print(request)
#     test_payment_intent = stripe.PaymentIntent.create(
#         amount=1000, 
#         currency='pln', 
#         payment_method_types=['card'],
#         receipt_email='test@example.com')
#     return Response(status=status.HTTP_200_OK, data=test_payment_intent)


class PaymentViewSet(viewsets.ModelViewSet):
    """view for manage the Room for the rental unit APIs"""
    serializer_class = serializers.PaymentDetailSerializer
    queryset = Payment.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly]
    
    def get_queryset(self):
        """retrieve locations for authenticated users"""
        return self.queryset.all().order_by('-id')   
    
    def get_serializer_class(self):
        """returns serializer class for request"""
        if self.action == 'list':
            return serializers.PaymentSerializer
        return self.serializer_class
    