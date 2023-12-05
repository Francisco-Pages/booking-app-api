"""Djanog admin customization"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin page for users"""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'), 
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )
    
admin.site.register(models.User, UserAdmin)
admin.site.register(models.RentalUnit)
admin.site.register(models.AmenitiesList)
admin.site.register(models.Location)
admin.site.register(models.Room)
admin.site.register(models.Pricing)
admin.site.register(models.Fee)
admin.site.register(models.Availability)
admin.site.register(models.CalendarEvent)
admin.site.register(models.Rulebook)
admin.site.register(models.Guidebook)
admin.site.register(models.Place)
admin.site.register(models.ReservationRequest)
admin.site.register(models.Reservation)
admin.site.register(models.CancellationRequest)
admin.site.register(models.ChangeRequest)
admin.site.register(models.Photo)
admin.site.register(models.Payment)
