# Generated by Django 4.1.6 on 2023-02-17 08:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_company_manufacturer_code'),
        ('warehouses', '0002_alter_warehouse_name_alter_warehouse_warehouse_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_owner', to='companies.company'),
        ),
    ]