# Generated by Django 4.1.6 on 2023-02-16 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_handlingunit_tht_warning_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='handlingunit',
            name='tht_warning_date',
            field=models.DateField(null=True),
        ),
    ]
