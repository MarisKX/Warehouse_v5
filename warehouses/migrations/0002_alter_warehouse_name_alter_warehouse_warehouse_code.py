# Generated by Django 4.1.6 on 2023-02-12 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='name',
            field=models.CharField(blank=True, default='warehouse', max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='warehouse_code',
            field=models.CharField(blank=True, default='0', max_length=2),
        ),
    ]
