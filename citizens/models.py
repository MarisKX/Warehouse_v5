from django.db import models
from django.conf import settings


# Create your models here.
class Citizen(models.Model):

    class Meta:
        verbose_name_plural = 'Citizens'

    first_name = models.CharField(max_length=254)
    first_name_display = models.CharField(max_length=254, blank=True, null=True)
    last_name = models.CharField(max_length=254)
    last_name_display = models.CharField(max_length=254, blank=True, null=True)
    bsn_number = models.PositiveIntegerField(
        blank=True, primary_key=True, default=1)
    street_adress_1 = models.IntegerField(default=0, blank=True)
    street_adress_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    post_code = models.CharField(max_length=6, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.last_name

    def get_full_name(self):
        return f"" + self.first_name_display + " " + self.last_name_display

    def get_house_number(self):
        return self.street_adress_1

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the citizen name and bsn
        if it hasn't been set already.
        """
        if self.bsn_number == 1:
            citizen_count = Citizen.objects.all().count()
            self.bsn_number = f"" + str(
                settings.CURRENT_YEAR) + str(
                    citizen_count + 1).zfill(3)
        self.first_name = self.first_name_display.replace(" ", "_").lower()
        self.last_name = self.last_name_display.replace(" ", "_").lower()
        super().save(*args, **kwargs)
