# Generated by Django 4.1.6 on 2023-02-09 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appsettings',
            name='iin_rate',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appsettings',
            name='uin_rate',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=4),
            preserve_default=False,
        ),
    ]
