from datetime import *
from django.utils import timezone
from datetime import timedelta, date
import datetime
from dateutil.relativedelta import *

from django.db import models
from django.shortcuts import render, get_object_or_404, reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from home.models import AppSettings
from companies.models import Company
from warehouses.models import Warehouse


class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=80)
    display_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_display_name(self):
        return self.display_name

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the category name
        """
        self.name = self.display_name.replace(" ", "_").lower()
        super().save(*args, **kwargs)


class SubCategory(models.Model):

    class Meta:
        verbose_name_plural = 'Subcategories'

    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=254)
    display_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_display_name(self):
        return self.display_name

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the subcategory name
        """
        self.name = self.display_name.replace(" ", "_").lower()
        super().save(*args, **kwargs)


class Product(models.Model):

    class Meta:
        ordering = ['name']

    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    subcategory = models.ForeignKey('SubCategory', null=True, blank=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=7, unique=True, default='AA001')
    name = models.CharField(max_length=100, default='name')
    display_name = models.CharField(max_length=100)
    paletizable = models.BooleanField(default=True)
    enviroment_tax_choices = [
        ('0', 'No Tax'),
        ('1', 'Class 1'),
        ('2', 'Class 2'),
        ('3', 'Class 3'),
        ('4', 'Class 4'),
    ]
    enviroment_tax_class = models.CharField(
        max_length=7, choices=enviroment_tax_choices, default='0')
    enviroment_tax_amount = models.DecimalField(
        max_digits=6, decimal_places=2, blank=False, null=False, default=0.00)
    expiry_end_date_terms = models.IntegerField(null=False, blank=False, default=0, validators=[MinValueValidator(0), MaxValueValidator(31)])
    expiry_end_date_choices_cat = [
        ('0', 'No End Date'),
        ('1', 'days'),
        ('2', 'weeks'),
        ('3', 'months'),
        ('4', 'years'),
        ('5', 'end of month + months'),
    ]
    expiry_end_date_cat = models.CharField(
        max_length=7, choices=expiry_end_date_choices_cat, default='0')
    units_per_package = models.IntegerField(null=False, blank=False, default=64, validators=[MinValueValidator(1), MaxValueValidator(64)])
    packages_per_lay = models.IntegerField(null=False, blank=False, default=9, validators=[MinValueValidator(9), MaxValueValidator(9)])
    lay_per_palet = models.IntegerField(null=False, blank=False, default=6, validators=[MinValueValidator(3), MaxValueValidator(6)])

    units_per_lay = models.IntegerField(null=False, blank=False)
    units_per_palet = models.IntegerField(null=False, blank=False)

    packages_per_palet = models.IntegerField(null=False, blank=False)

    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the article
        """
        if self.name == 'name':
            self.name = self.display_name.replace(" ", "_").lower()
        if self.code == 'AA001':
            same_cat_products_count = Product.objects.filter(subcategory=self.subcategory).count()
            self.code = (
                self.category.name[0].upper() +
                self.category.name[1].upper() +
                self.subcategory.name[0].upper() +
                self.subcategory.name[1].upper() +
                str(same_cat_products_count + 1).zfill(3)
                )
            check_for_dubble_entries = Product.objects.filter(name=self.name).count()
            if check_for_dubble_entries == 0:
                self.units_per_lay = self.units_per_package * self.packages_per_lay
                self.units_per_palet = self.units_per_lay * self.lay_per_palet
                self.packages_per_palet = self.packages_per_lay * self.lay_per_palet
                current_settings = get_object_or_404(AppSettings, valid=True)
                enviroment_tax_base = current_settings.enviroment_tax_base
                self.enviroment_tax_amount = int(self.enviroment_tax_class) * enviroment_tax_base
                super().save(*args, **kwargs)
        else:
            self.units_per_lay = self.units_per_package * self.packages_per_lay
            self.units_per_palet = self.units_per_lay * self.lay_per_palet
            self.packages_per_palet = self.packages_per_lay * self.lay_per_palet
            current_settings = get_object_or_404(AppSettings, valid=True)
            enviroment_tax_base = current_settings.enviroment_tax_base
            self.enviroment_tax_amount = int(self.enviroment_tax_class) * enviroment_tax_base
            super().save(*args, **kwargs)


class HandlingUnit(models.Model):
    manufacturer = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(Warehouse, null=True, blank=True, on_delete=models.SET_NULL, related_name="warehouse")
    product = models.ForeignKey('Product', null=True, blank=True, on_delete=models.SET_NULL)
    qty = models.IntegerField(default=1, blank=True)
    units = [
        ('0', 'Units'),
        ('1', 'Packages'),
    ]
    qty_units = models.CharField(
        max_length=7, choices=units, default='0')
    hu = models.CharField(max_length=20, blank=False, null=False, default="0")
    batch_nr = models.CharField(max_length=9, blank=True, null=True)
    release_date = models.DateField(auto_now_add=False)
    tht_warning_date = models.DateField(auto_now_add=False, null=True)
    tht = models.DateField(auto_now_add=False, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.hu

    def save(self, *args, **kwargs):
        if self.hu == "0":
            hu_count = HandlingUnit.objects.filter(manufacturer=self.manufacturer, location=self.location).count()
            hu_pre_code = get_object_or_404(Warehouse, name=self.location).warehouse_code
            self.hu = f"" + hu_pre_code + str(hu_count + 1).zfill(15)
        product_tht_int = get_object_or_404(Product, name=self.product).expiry_end_date_terms
        product_tht_let = get_object_or_404(Product, name=self.product).expiry_end_date_cat
        if product_tht_let == "1":
            self.tht = self.release_date + timedelta(days=product_tht_int)
            self.tht_warning_date = self.tht - timedelta(days=2)
        elif product_tht_let == "2":
            self.tht = self.release_date + timedelta(weeks=product_tht_int)
            self.tht_warning_date = self.tht - timedelta(days=5)
        elif product_tht_let == "3":
            self.tht = self.release_date + relativedelta(months=+product_tht_int)
            self.tht_warning_date = self.tht - timedelta(days=15)
        elif product_tht_let == "4":
            self.tht = self.release_date + relativedelta(years=+product_tht_int)
            self.tht_warning_date = self.tht - timedelta(days=45)
        elif product_tht_let == "5":
            self.tht = self.release_date + relativedelta(months=+product_tht_int) + relativedelta(day=31)
            self.tht_warning_date = self.tht - timedelta(days=90)

        super().save(*args, **kwargs)


class HandlingUnitMovement(models.Model):
    hu = models.ForeignKey(HandlingUnit, null=False, blank=False, on_delete=models.CASCADE, related_name="main_hu")
    date = models.DateField(auto_now_add=False)
    doc_nr = models.CharField(max_length=20, blank=False, null=False, default="0")
    qty = models.IntegerField(default=0, blank=False, null=False)
    from_location = models.CharField(max_length=60, blank=False, null=False, default="0")
    from_hu = models.CharField(max_length=60, blank=False, null=False, default="")
    to_location = models.CharField(max_length=60, blank=False, null=False, default="0")
    to_hu = models.CharField(max_length=60, blank=False, null=False, default="")