# Generated by Django 4.1.6 on 2023-03-10 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('real_estate', '0005_realestatetypes_coef_of_cadastre_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='realestate',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
