"""
Database models
"""
from datetime import time
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MinValueValidator, MaxValueValidator

def rental_unit_image_file_path(instance, filename):
    """Generate file path for new rental unit image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'rentalunit', filename)

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
    # is_superuser = models.BooleanField(default=False)
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
UNIT_CHOICES = (
    ('Hotel', 'hotel'),
    ('Apartment', 'apartment'),
    ('House', 'house'),
    ('Room', 'room'),
    ('Trailer', 'trailer'),
    ('Igloo', 'igloo'),
    ('Villa', 'villa'),
)
    
class RentalUnit(models.Model):
    """Rental unit objects."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, default='Enter Title')
    description = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=255, default='en,')
    status = models.BooleanField(default=True)
    image = models.ImageField(null=True, upload_to=rental_unit_image_file_path)
    unit_type = models.CharField(max_length=30, choices=UNIT_CHOICES, default='hotel')
    max_guests = models.IntegerField(default=1)
    
    def __str__(self):
        return self.title
    
    
class AmenitiesList(models.Model):
    """list of amenities available for rental units"""
    rental_unit = models.OneToOneField(RentalUnit, primary_key=True, on_delete=models.CASCADE)
    popular_essentials = models.BooleanField(default=False)
    popular_airconditioning = models.BooleanField(default=False)
    popular_cleaning_products = models.BooleanField(default=False)
    popular_cooking_basics = models.BooleanField(default=False)
    popular_dedicated_workspace = models.BooleanField(default=False)
    popular_dishes_and_silverware = models.BooleanField(default=False)
    popular_washer = models.BooleanField(default=False)
    popular_dryer = models.BooleanField(default=False)
    popular_hair_dryer = models.BooleanField(default=False)
    popular_heating = models.BooleanField(default=False)
    popular_hot_tub = models.BooleanField(default=False)
    popular_kitchen = models.BooleanField(default=False)
    popular_pool = models.BooleanField(default=False)
    popular_tv = models.BooleanField(default=False)
    popular_wifi = models.BooleanField(default=False)
    bathroom_bathtub = models.BooleanField(default=False)
    bathroom_bidet = models.BooleanField(default=False)
    bathroom_body_soap = models.BooleanField(default=False)
    bathroom_conditioner = models.BooleanField(default=False)
    bathroom_hot_water_outdoor_shower = models.BooleanField(default=False)
    bathroom_shampoo = models.BooleanField(default=False)
    bathroom_shower_gel = models.BooleanField(default=False)
    bedroom_essentials = models.BooleanField(default=False)
    bedroom_bed_linens = models.BooleanField(default=False)
    bedroom_clothing_storage = models.BooleanField(default=False)
    bedroom_extra_pillows_and_blankets = models.BooleanField(default=False)
    bedroom_hangers = models.BooleanField(default=False)
    bedroom_iron = models.BooleanField(default=False)
    bedroom_drying_rack = models.BooleanField(default=False)
    bedroom_mosquito_net = models.BooleanField(default=False)
    bedroom_room_darkening_shades = models.BooleanField(default=False)
    bedroom_safe = models.BooleanField(default=False)
    entertainment_arcade_games = models.BooleanField(default=False)
    entertainment_books_and_reading_material = models.BooleanField(default=False)
    entertainment_bowling_alley = models.BooleanField(default=False)
    entertainment_climbing_wall = models.BooleanField(default=False)
    entertainment_ethernet_connection = models.BooleanField(default=False)
    entertainment_exercise_equipment = models.BooleanField(default=False)
    entertainment_games_console = models.BooleanField(default=False)
    entertainment_life_size_games = models.BooleanField(default=False)
    entertainment_piano = models.BooleanField(default=False)
    entertainment_ping_pong_table = models.BooleanField(default=False)
    entertainment_record_player = models.BooleanField(default=False)
    entertainment_sound_system = models.BooleanField(default=False)
    family_baby_bath = models.BooleanField(default=False)
    family_baby_monitor = models.BooleanField(default=False)
    family_childrens_bikes = models.BooleanField(default=False)
    family_childrens_playroom = models.BooleanField(default=False)
    family_baby_safe_gates = models.BooleanField(default=False)
    family_changing_table = models.BooleanField(default=False)
    family_childrens_books_and_toys = models.BooleanField(default=False)
    family_childrens_dinnerware = models.BooleanField(default=False)
    family_crib = models.BooleanField(default=False)
    family_fireplace_guards = models.BooleanField(default=False)
    family_high_chair = models.BooleanField(default=False)
    family_outdoor_playground = models.BooleanField(default=False)
    family_packnplay_travel_crib = models.BooleanField(default=False)
    family_table_corner_guards = models.BooleanField(default=False)
    family_window_guards = models.BooleanField(default=False)
    heating_and_cooling_ceiling_fan = models.BooleanField(default=False)
    heating_and_cooling_heating = models.BooleanField(default=False)
    heating_and_cooling_indoor_fireplace = models.BooleanField(default=False)
    heating_and_cooling_portable_fans = models.BooleanField(default=False)
    kitchen_baking_sheet = models.BooleanField(default=False)
    kitchen_bbq_utensils = models.BooleanField(default=False)
    kitchen_breadmaker = models.BooleanField(default=False)
    kitchen_blender = models.BooleanField(default=False)
    kitchen_coffee = models.BooleanField(default=False)
    kitchen_coffee_maker = models.BooleanField(default=False)
    kitchen_dining_table = models.BooleanField(default=False)
    kitchen_dishwasher = models.BooleanField(default=False)
    kitchen_freezer = models.BooleanField(default=False)
    kitchen_hot_water_kettle = models.BooleanField(default=False)
    kitchen_kitchenette = models.BooleanField(default=False)
    kitchen_microwave = models.BooleanField(default=False)
    kitchen_mini_fridge = models.BooleanField(default=False)
    kitchen_oven = models.BooleanField(default=False)
    kitchen_refrigerator = models.BooleanField(default=False)
    kitchen_rice_maker = models.BooleanField(default=False)
    kitchen_stove = models.BooleanField(default=False)
    kitchen_toaster = models.BooleanField(default=False)
    kitchen_trash_compactor = models.BooleanField(default=False)
    kitchen_wine_glasses = models.BooleanField(default=False)
    location_features_beach_access = models.BooleanField(default=False)
    location_features_lake_acccess = models.BooleanField(default=False)
    location_features_laundromat_nearby = models.BooleanField(default=False)
    location_features_private_entrance = models.BooleanField(default=False)
    location_features_resort_access = models.BooleanField(default=False)
    location_features_ski_access = models.BooleanField(default=False)
    location_features_waterfront = models.BooleanField(default=False)
    outdoor_backyard = models.BooleanField(default=False)
    outdoor_bbq_grill = models.BooleanField(default=False)
    outdoor_beach_essentials = models.BooleanField(default=False)
    outdoor_bikes = models.BooleanField(default=False)
    outdoor_boat_slip = models.BooleanField(default=False)
    outdoor_fire_pit = models.BooleanField(default=False)
    outdoor_hammock = models.BooleanField(default=False)
    outdoor_kayak = models.BooleanField(default=False)
    outdoor_dining_area = models.BooleanField(default=False)
    outdoor_furniture = models.BooleanField(default=False)
    outdoor_kitchen = models.BooleanField(default=False)
    outdoor_patio_or_balcony = models.BooleanField(default=False)
    outdoor_sun_loungers = models.BooleanField(default=False)
    parking_and_facilities_elevator = models.BooleanField(default=False)
    parking_and_facilities_ev_charger = models.BooleanField(default=False)
    parking_and_facilities_free_parking_on_premise = models.BooleanField(default=False)
    parking_and_facilities_free_street_parking = models.BooleanField(default=False)
    parking_and_facilities_paid_parking_off_premises = models.BooleanField(default=False)
    parking_and_facilities_paid_parking_on_premises = models.BooleanField(default=False)
    parking_and_facilities_gym = models.BooleanField(default=False)
    parking_and_facilities_sauna = models.BooleanField(default=False)
    parking_and_facilities_single_level_home = models.BooleanField(default=False)
    services_breakfast = models.BooleanField(default=False)
    services_cleaning_available_during_stay = models.BooleanField(default=False)
    services_long_term_stays_allowed = models.BooleanField(default=False)
    services_luggage_dropoff_allowed = models.BooleanField(default=False)
    accessibility_entrance = models.BooleanField(default=False)
    accessibility_parking = models.BooleanField(default=False)
    accessibility_lavatory_equipment = models.BooleanField(default=False)
    accessibility_wide_doors = models.BooleanField(default=False)
    accessibility_stairs = models.BooleanField(default=False)
    safety_carbon_monoxide_alarm = models.BooleanField(default=False)
    safety_fire_extinguisher = models.BooleanField(default=False)
    safety_first_aid_kit = models.BooleanField(default=False)
    safety_smoke_alarm = models.BooleanField(default=False)
    safety_unsuitable_for_children_2_12 = models.BooleanField(default=False)
    safety_unsuitable_for_infants_under_2 = models.BooleanField(default=False)
    safety_pool_or_hot_tub_without_gate_or_lock = models.BooleanField(default=False)
    safety_nearby_body_of_water = models.BooleanField(default=False)
    safety_climbing_or_play_structure = models.BooleanField(default=False)
    safety_heights_without_rails = models.BooleanField(default=False)
    safety_dangerous_animals = models.BooleanField(default=False)
    safety_security_cameras = models.BooleanField(default=False)
    safety_audio_recording_devices = models.BooleanField(default=False)
    safety_must_climb_stairs = models.BooleanField(default=False)
    safety_potential_for_noise = models.BooleanField(default=False)
    safety_pet_in_property = models.BooleanField(default=False)
    safety_no_parking_on_property = models.BooleanField(default=False)
    safety_some_spaces_are_shared = models.BooleanField(default=False)
    safety_weapons_on_property = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Amenities for rental unit #{self.rental_unit.id}."
    
class Location(models.Model):
    """Location details of a rental unit"""
    rental_unit = models.OneToOneField(RentalUnit, primary_key=True, on_delete=models.CASCADE)
    neighborhood_description = models.TextField(default="Describe the neighborhood of your place.")
    getting_around = models.TextField(default="Any tips about how to reach your place.")
    location_sharing = models.BooleanField(default=False)
    address1 = models.CharField(verbose_name="Address line 1", max_length=1024, blank=True)
    address2 = models.CharField(verbose_name="Address line 2",max_length=1024, blank=True)
    zip_code = models.CharField(verbose_name="ZIP / Postal code",max_length=12, blank=True)
    city = models.CharField(verbose_name="City",max_length=1024, blank=True)
    country = models.CharField(verbose_name="Country",max_length=3, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    
    def __str__(self):
        return f"Location for rental unit #{self.rental_unit.id}."
    
ROOM_TYPE_CHOICES = (
    ('Bedroom', 'bedroom'),
    ('Living room', 'living room'),
    ('Game room', 'game room'),
    ('Family room', 'family room'),
    ('Studio', 'studio'),
    ('Office', 'office'),
    ('Bathroom (full)', 'bathroom (full)'),
    ('Bathroom (half)', 'bathroom (half)'),
    ('Loft', 'loft'),
    ('Basement', 'basement'),
)
BED_TYPE_CHOICES = (
    ('King', 'king'),
    ('Queen', 'queen'),
    ('Full', 'Full'),
    ('Twin', 'twin'),
    ('Single', 'single'),
    ('Crib', 'crib'),
)


class Room(models.Model):
    """a room or space in a rental unit"""
    rental_unit = models.OneToOneField(RentalUnit, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    room_type = models.CharField(max_length=20,choices=ROOM_TYPE_CHOICES, blank=True)
    bed_type = models.CharField(max_length=20,choices=BED_TYPE_CHOICES, blank=True)
    tv = models.BooleanField(default=False)
    accessible = models.BooleanField(default=False)
    
CURRENCY_CHOICES = (
    ('USD', 'USD'),
    ('GBP', 'GBP'),
    ('YEN', 'YEN'),
)

class Pricing(models.Model):
    """pricing details for a rental unit"""
    rental_unit = models.OneToOneField(RentalUnit, primary_key=True, on_delete=models.CASCADE)
    night_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    smart_pricing = models.BooleanField(default=False)
    min_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.CharField(max_length=30, choices=CURRENCY_CHOICES, default='USD')
    week_discount = models.IntegerField(default=0)
    month_discount = models.IntegerField(default=0)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
FEE_CHOICES = (
    ('Pet', 'pet'),
    ('Transport', 'transport'),
    ('Extra guest', 'extra guest'),
)
    
class Fee(models.Model):
    """a detailed fee charged by a rental unit"""
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, choices=FEE_CHOICES, blank=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('rental_unit', 'name',)
        
        
class Availability(models.Model):
    """availability preferences for a rental unit"""
    rental_unit = models.OneToOneField(RentalUnit, primary_key=True, on_delete=models.CASCADE)
    min_stay = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(7)
        ],
        default=1
    )
    max_stay = models.IntegerField(
        validators=[
            MinValueValidator(8),
            MaxValueValidator(90)
        ],
        default=90
    )
    min_notice = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(30)
        ],
        default=1
    )
    max_notice = models.IntegerField(
        validators=[
            MinValueValidator(31),
            MaxValueValidator(365)
        ],
        default=365
    )
    prep_time = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ],
        default=0
    )
    instant_booking = models.BooleanField(default=False)


EVENT_CHOICES = (
    ('Reservation', 'reservation'),
    ('Blocked', 'blocked'),
)
    
class CalendarEvent(models.Model):
    """a log of an event happening in a rental unit"""
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE, null=True)
    reason = models.CharField(max_length=50, choices=EVENT_CHOICES, blank=False)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)


CANCELLATION_CHOICES = (
    ('Flexible', 'flexible'),
    ('Moderate', 'moderate'),
    ('Firm', 'firm'),
    ('Strict', 'strict'),
    ('Firm Long Term', 'firm long Term'),
    ('Strict Long Term', 'strict long Term'),
    ('Super Strict 30', 'super strict 30'),
    ('Non-refundable', 'non-refundable'),
)


class Rulebook(models.Model):
    """a rule book for a rental unit"""
    rental_unit = models.OneToOneField(RentalUnit, primary_key=True, on_delete=models.CASCADE)
    cancellation_policy = models.CharField(max_length=50, choices=CANCELLATION_CHOICES, default='Flexible')
    house_rules = models.TextField(blank=True)
    pets_allowed = models.BooleanField(default=False)
    events_allowed = models.BooleanField(default=False)
    smoking_allowed = models.BooleanField(default=False)
    commercial_photo_film_allowed = models.BooleanField(default=False)
    guest_requirements = models.TextField(blank=True)
    laws_and_regulations = models.TextField(blank=True)
    

CHECK_IN_METHOD_CHOICES = (
    ('Smart lock', 'smart lock'),
    ('Keypad', 'keypad'),
    ('Lockbox', 'lockbox'),
    ('Building Staff', 'Building staff'),
    ('Host greets you', 'host greets you'),
) 
    
class Guidebook(models.Model):
    """booking information for guests"""
    rental_unit = models.OneToOneField(RentalUnit, primary_key=True, on_delete=models.CASCADE)
    check_in_start_time = models.TimeField(auto_now=False, auto_now_add=False, default=time(hour=12, minute=0))
    check_in_end_time = models.TimeField(auto_now=False, auto_now_add=False, default=time(hour=18, minute=0), null=True)
    check_out_time = models.TimeField(auto_now=False, auto_now_add=False, default=time(hour=10, minute=0))
    check_in_method = models.CharField(max_length=255, choices=CHECK_IN_METHOD_CHOICES, default='Host greets you')
    check_in_instructions = models.TextField(blank=True)
    check_out_instructions = models.TextField(blank=True)
    house_manual = models.TextField(default='Tell your guests about how things work at your place.', blank=True)
    
    
CATEGORY_CHOICES = (
    ('Restaurant', 'restaurant'),
    ('Night Club', 'night club'),
    ('Beach', 'beach')
)

class Place(models.Model):
    """A place of interest"""
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, blank=False)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES, blank=False)
    description = models.TextField(blank=True)
    address1 = models.CharField(verbose_name="Address line 1", max_length=1024, blank=True)
    address2 = models.CharField(verbose_name="Address line 2", max_length=1024, blank=True)
    zip_code = models.CharField(verbose_name="ZIP / Postal code", max_length=12, blank=True)
    city = models.CharField(verbose_name="City", max_length=1024, blank=True)
    country = models.CharField(verbose_name="Country", max_length=3, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0, blank=True)
    
    
class ReservationRequest(models.Model):
    """a user request to make a reservation"""
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    check_in = models.DateField()
    check_out = models.DateField() 
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    
    
class Reservation(models.Model):
    """a reservation made by a guest for a rental unit"""
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE, null=True)
    reservation_request = models.OneToOneField(ReservationRequest, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    check_in = models.DateField()
    check_out = models.DateField() 
    nights = models.IntegerField(null=True) 
    night_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    taxes = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ]
    )
    total = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    status = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    # def get_nightly_subtotal(self):
    #     """get the nightly subtotal for the reservation"""
    #     delta = self.end_date - self.start_date 
    #     subtotal = delta.days * self.night_price
    #     return subtotal
    

class CancellationRequest(models.Model):
    """a user request to cancel a confirmed reservation"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    refund = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ]                            
    )
    
class ChangeRequest(models.Model):
    """a user request to cancel a confirmed reservation"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    new_check_in = models.DateField()
    new_check_out = models.DateField()
    status = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    