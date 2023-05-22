from django.db.models.signals import post_save, post_delete, pre_delete, m2m_changed
from django.dispatch import receiver

from models import RentalUnit, Amenities


# @receiver(post_save, sender=RentalUnit)
# def create_amenities_list(sender, instance, created, **kwargs):
#     if created:
#         created_rental_unit = RentalUnit.objects.get(instance)
#         created_amenities_list = Amenities.objects.create(rental_unit=created_rental_unit)
#         created_rental_unit.amenities = create_amenities_list
#         created_rental_unit.save()
#         created_amenities_list.save()