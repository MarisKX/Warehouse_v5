# Generated by Django 4.1.6 on 2023-02-19 14:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_handlingunit_company_alter_handlingunit_manufacturer'),
        ('companies', '0005_alter_company_owner'),
        ('warehouses', '0003_alter_warehouse_company'),
        ('invoices', '0008_alter_invoice_invoice_paid_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_number', models.CharField(default='TO00001', max_length=10)),
                ('date', models.DateField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_transfer_order', to='companies.company')),
                ('warehouse_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_order_from_warehouse', to='warehouses.warehouse')),
                ('warehouse_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_order_to_warehouse', to='warehouses.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='TransferOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_with_to', to='products.product')),
                ('to_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_transfer_order_from', to='invoices.transferorder')),
            ],
        ),
    ]