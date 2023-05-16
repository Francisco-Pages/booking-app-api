"""
Serializers for the user API view.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)

from rest_framework import serializers

from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    """serializers for the user model"""
    
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}
        
    def create(self, validated_data):
        """Create and return a user with an encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
    
class AuthTokenSerializer(serializers.Serializer):
    """serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace=False,
    )
    
    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            message = _('Unable to authenticate with credentials provided')
            raise serializers.ValidationError(message, code='authorization')
        
        attrs['user'] = user
        
        return attrs
    