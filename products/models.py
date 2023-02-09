from django.db import models
from django.shortcuts import render, get_object_or_404, reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from home.models import AppSettings


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
        current_settings = get_object_or_404(AppSettings, valid=True)
        enviroment_tax_base = current_settings.enviroment_tax_base
        print(self.enviroment_tax_class)
        self.enviroment_tax_amount = int(self.enviroment_tax_class) * enviroment_tax_base
        super().save(*args, **kwargs)
