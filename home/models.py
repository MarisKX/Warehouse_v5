from django.db import models
from django.conf import settings
from datetime import *
from django.utils import timezone


# Create your models here.
class AppSettings(models.Model):

    class Meta:
        verbose_name_plural = "Basic Settings"

    settings_number = models.CharField(max_length=8, default='0000xxxx')
    valid_from = models.DateField(auto_now_add=False)
    valid_till = models.DateField(auto_now_add=False)
    acions_per_day = models.PositiveIntegerField(default=1)
    vsaoi_dn = models.DecimalField(
        max_digits=4, decimal_places=2, blank=False, null=False)
    iin_rate = models.DecimalField(
        max_digits=4, decimal_places=2, blank=False, null=False)
    no_iin_level = models.DecimalField(
        max_digits=8, decimal_places=2, blank=False, null=False)
    uin_rate = models.DecimalField(
        max_digits=4, decimal_places=2, blank=False, null=False)
    enviroment_tax_base = models.DecimalField(
        max_digits=8, decimal_places=2, blank=False, null=False)
    btw = models.DecimalField(
        max_digits=8, decimal_places=2, blank=False, null=False)
    vsaoi_dd = models.DecimalField(
        max_digits=4, decimal_places=2, blank=False, null=False)
    base_cadastre_value = models.DecimalField(
        max_digits=4, decimal_places=2, blank=False, null=False)
    valid = models.BooleanField()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the bsettings number
        if it hasn't been set already.
        """
        if self.settings_number == "0000xxxx":
            settings_count = AppSettings.objects.all().count()
            if settings_count > 0:
                previous_settings = AppSettings.objects.latest('valid_till')
                previous_settings.valid = False
                previous_settings.save(update_fields=['valid'])
                print(previous_settings.valid)
            self.settings_number = f"" + str(
                settings.CURRENT_YEAR) + str(
                    settings_count + 1).zfill(4)
        super().save(*args, **kwargs)
