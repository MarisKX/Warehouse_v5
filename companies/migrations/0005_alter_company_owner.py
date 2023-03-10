# Generated by Django 4.1.6 on 2023-02-17 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('citizens', '0003_alter_citizen_first_name'),
        ('companies', '0004_company_manufacturer_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='citizens.citizen'),
        ),
    ]
