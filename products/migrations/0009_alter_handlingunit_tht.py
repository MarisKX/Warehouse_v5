# Generated by Django 4.1.6 on 2023-02-13 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_alter_handlingunit_tht'),
    ]

    operations = [
        migrations.AlterField(
            model_name='handlingunit',
            name='tht',
            field=models.DateField(null=True),
        ),
    ]
