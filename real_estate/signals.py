from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import RealEstate, RealEstateCoordinates, RealEstateTypes
from home.models import AppSettings


# Update real estate details on save and/or delete
@receiver(post_save, sender=RealEstate)
def create_on_save(sender, instance, created, **kwargs):
    """
    Create Invoice number
    """
    if instance.cadastre_number == '':
        property_count = RealEstate.objects.all().count() or 0
        self.cadastre_number = self.city[0:3].upper() + str(property_count + 1).zfill(5)
        instance.save()


@receiver(post_save, sender=RealEstateCoordinates)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.real_estate.update_field_size()


@receiver(post_delete, sender=RealEstateCoordinates)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.real_estate.update_field_size()


# Update real estate details on save and/or delete
@receiver(post_save, sender=AppSettings)
def update_cadastre_values_on_new_settings(sender, instance, created, **kwargs):
    """
    Create Invoice number
    """
    all_real_estates = RealEstate.objects.filter(active=True)
    for real_estate in all_real_estates:
        real_estate.save()
