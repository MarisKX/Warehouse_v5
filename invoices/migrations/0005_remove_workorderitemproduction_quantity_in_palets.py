# Generated by Django 4.1.6 on 2023-02-13 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0004_workorderitemproduction_quantity_in_palets'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workorderitemproduction',
            name='quantity_in_palets',
        ),
    ]
