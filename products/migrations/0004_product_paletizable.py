# Generated by Django 4.1.6 on 2023-02-10 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_lay_per_palet_product_packages_per_lay_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='paletizable',
            field=models.BooleanField(default=True),
        ),
    ]