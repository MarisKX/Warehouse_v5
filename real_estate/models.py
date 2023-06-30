from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from companies.models import Company
from citizens.models import Citizen
from home.models import AppSettings

# Create your models here.


class RealEstateTypes(models.Model):
    name = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    coef_of_cadastre_value = models.DecimalField(
        max_digits=4, decimal_places=2, blank=False, null=False)
    color = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = 'Real Estate Types'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the category name
        """
        self.name = self.display_name.replace(" ", "_").lower()
        super().save(*args, **kwargs)


class RealEstate(models.Model):

    class Meta:
        verbose_name_plural = 'Real Estate'

    owner_com = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='real_estate_owner_com')
    owner_pp = models.ForeignKey(Citizen, null=True, blank=True, on_delete=models.CASCADE, related_name='real_estate_owner_pp')
    property_type = models.ForeignKey(RealEstateTypes, null=False, blank=False, on_delete=models.CASCADE, related_name='real_estate_type')
    cadastre_number = models.CharField(max_length=8, blank=False, primary_key=True)
    street_adress_1 = models.IntegerField(default=0, blank=True, null=True)
    street_adress_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    post_code = models.CharField(max_length=6, blank=True)
    country = models.CharField(max_length=100, blank=True)
    field_size = models.IntegerField(default=0, blank=True)
    center_coordinates_min_E = models.IntegerField(default=0, blank=False)
    center_coordinates_min_S = models.IntegerField(default=0, blank=False)
    cadastre_value = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.cadastre_number)

    def update_field_size(self):
        self.field_size = self.real_estate.aggregate(
            Sum('field_size_element'))['field_size_element__sum']
        super().save()

    def save(self, *args, **kwargs):
        current_settings = get_object_or_404(AppSettings, valid=True)
        cadastre_base_value = current_settings.base_cadastre_value
        prop_type = get_object_or_404(RealEstateTypes, name=self.property_type)
        coef_of_type = prop_type.coef_of_cadastre_value
        self.cadastre_value = cadastre_base_value * coef_of_type * self.field_size

        super().save(*args, **kwargs)


class RealEstateCoordinates(models.Model):
    real_estate = models.ForeignKey(RealEstate, null=True, blank=False, on_delete=models.CASCADE, related_name='real_estate')
    coordinates_min_E = models.IntegerField(default=0, blank=False)
    coordinates_min_S = models.IntegerField(default=0, blank=False)
    coordinates_max_E = models.IntegerField(default=0, blank=False)
    coordinates_max_S = models.IntegerField(default=0, blank=False)
    width = models.IntegerField(default=0, blank=False)
    height = models.IntegerField(default=0, blank=False)
    field_size_element = models.IntegerField(default=0, blank=True)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the cadastre number
        if it hasn't been set already.
        """
        self.width = self.coordinates_max_E - self.coordinates_min_E + 10
        self.height = self.coordinates_max_S - self.coordinates_min_S + 10
        self.field_size_element = self.width * self.height / 100
        super().save(*args, **kwargs)


class RealEstateOwnerHistory(models.Model):
    real_estate_object = models.ForeignKey(RealEstate, null=True, blank=True, on_delete=models.CASCADE, related_name='real_estate_object')
    owner_com = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='real_estate_owner_com_h')
    owner_pp = models.ForeignKey(Citizen, null=True, blank=True, on_delete=models.CASCADE, related_name='real_estate_owner_pp_h')
    date_of_purchase = models.DateField(auto_now_add=False)
    cadastre_value_of_purchase = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    date_of_sale = models.DateField(blank=True, null=True)
    cadastre_value_of_sale = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    sales_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)


class MinecraftMap(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    file = models.FileField()
