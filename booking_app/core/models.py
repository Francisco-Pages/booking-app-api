"""
Database models
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('Please enter an email address.')
        
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
    
        return user
    
    def create_superuser(self, email, password):
        """create and return a superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
UNIT_CHOICES = (
    ('Hotel', 'hotel'),
    ('Apartment', 'apartment'),
    ('House', 'house'),
    ('Room', 'room'),
    ('Trailer', 'trailer'),
    ('Igloo', 'igloo')
)
STATUS_CHOICES = (
    ('Active', 'active'),
    ('Inactive', 'inactive')
)
    
class RentalUnit(models.Model):
    """Rental unit objects."""
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    unit_type = models.CharField(max_length=30, choices=UNIT_CHOICES, default='hotel')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    
    def __str__(self):
        return self.title
    
    