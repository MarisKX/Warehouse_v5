# Generated by Django 4.1.6 on 2023-02-20 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_handlingunit_company_alter_handlingunit_manufacturer'),
        ('companies', '0005_alter_company_owner'),
        ('warehouses', '0003_alter_warehouse_company'),
        ('invoices', '0011_retailsale_retailsaleitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConstructionInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_invoice_number', models.CharField(default='C1', max_length=12)),
                ('date', models.DateField()),
                ('construction_completed', models.BooleanField(default=True)),
                ('payment_term', models.CharField(choices=[('14', '14 days'), ('21', '21 day'), ('30', '30 days'), ('60', '60 days'), ('90', '90 days')], default='21', max_length=10)),
                ('c_invoice_paid', models.BooleanField()),
                ('c_invoice_paid_confirmed', models.BooleanField()),
                ('mat_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('lab_costs_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('amount_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('btw_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('amount_total_with_btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('build_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='build_customer', to='companies.company')),
                ('constructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constructor', to='companies.company')),
                ('constructor_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constructor_warehouse', to='warehouses.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='ConstructionInvoiceLabourCosts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_decription', models.CharField(max_length=100)),
                ('quantity', models.IntegerField(default=0)),
                ('measure_unit', models.CharField(choices=[('1', 'm2'), ('2', 'm3'), ('3', 'pcs')], default='3', max_length=3)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('construction_labour_item_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6)),
                ('btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('construction_labour_item_total_with_btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('c_invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='construction_labour', to='invoices.constructioninvoice')),
            ],
        ),
        migrations.CreateModel(
            name='ConstructionInvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('constructionitem_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6)),
                ('btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('constructionitem_total_with_btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('c_invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constructionitems', to='invoices.constructioninvoice')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
    ]
