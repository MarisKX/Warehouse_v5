# Generated by Django 4.1.6 on 2023-02-16 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_handlingunitmovement_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='handlingunit',
            name='empty',
            field=models.BooleanField(default=False),
        ),
    ]