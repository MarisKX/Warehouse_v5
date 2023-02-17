from django.db import models
from django.shortcuts import get_object_or_404
from companies.models import Company


# Create your models here.
class Warehouse(models.Model):
    company = models.ForeignKey(
        Company,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name='warehouse_owner')
    name = models.CharField(max_length=254, blank=True, null=True, default="warehouse")
    display_name = models.CharField(max_length=254, blank=True)
    warehouse_code = models.CharField(default="0", max_length=2, blank=True)
    internal_warehouse = models.BooleanField(default=False)
    street_adress_1 = models.IntegerField(default=0, blank=True)
    street_adress_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    post_code = models.CharField(max_length=6, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the warehouse name and codes
        if it hasn't been set already.
        """
        warehouse_count = Warehouse.objects.filter(company=self.company).count()
        warehouse_owner = get_object_or_404(Company, name=self.company)
        self.warehouse_code = f"" + str(warehouse_owner.manufacturer_code) + str(warehouse_count + 1).zfill(2)
        self.name = self.display_name.replace(" ", "_").lower()
        super().save(*args, **kwargs)
