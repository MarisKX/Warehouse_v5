# Generated by Django 4.1.6 on 2023-02-13 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0003_workorderitemproduction_quantity_in_units'),
    ]

    operations = [
        migrations.AddField(
            model_name='workorderitemproduction',
            name='quantity_in_palets',
            field=models.IntegerField(default=0),
        ),
    ]