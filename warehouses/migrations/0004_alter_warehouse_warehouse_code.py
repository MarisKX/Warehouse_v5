# Generated by Django 4.1.6 on 2023-02-23 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0003_alter_warehouse_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='warehouse_code',
            field=models.CharField(blank=True, default='0', max_length=6),
        ),
    ]
