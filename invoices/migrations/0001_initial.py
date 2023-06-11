# Generated by Django 4.1.6 on 2023-06-11 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0005_alter_company_owner'),
        ('products', '0017_handlingunit_hu_issued_by'),
        ('citizens', '0003_alter_citizen_first_name'),
        ('warehouses', '0004_alter_warehouse_warehouse_code'),
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
                ('build_customer_com', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='build_customer_com', to='companies.company')),
                ('build_customer_pp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='build_customer_pp', to='citizens.citizen')),
                ('constructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constructor', to='companies.company')),
                ('constructor_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constructor_warehouse', to='warehouses.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(default='AA00001', max_length=8)),
                ('date', models.DateField()),
                ('payment_term_options', models.CharField(choices=[('7', '7 days'), ('14', '14 days'), ('21', '21 day'), ('30', '30 days'), ('60', '60 days')], default='14', max_length=10)),
                ('payment_term', models.DateField(null=True)),
                ('invoice_paid', models.BooleanField(default=False)),
                ('invoice_paid_confirmed', models.BooleanField(default=False)),
                ('amount_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('btw_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('amount_total_with_btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='companies.company')),
                ('customer_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_warehouse', to='warehouses.warehouse')),
                ('suplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suplier', to='companies.company')),
                ('suplier_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suplier_warehouse', to='warehouses.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='RetailSale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('retail_sale_number', models.CharField(default='RT1', max_length=12)),
                ('date', models.DateField()),
                ('retail_sale_paid', models.BooleanField()),
                ('retail_sale_paid_confirmed', models.BooleanField()),
                ('amount_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('btw_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('amount_total_with_btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='citizens.citizen')),
                ('retailer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retailer', to='companies.company')),
                ('retailer_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retailer_warehouse', to='warehouses.warehouse')),
            ],
        ),
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
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_order_number', models.CharField(default='WO00001', max_length=10)),
                ('date', models.DateField()),
                ('enviroment_tax_on_workorder_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_work_order', to='companies.company')),
                ('warehouse_production', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_warehouse', to='warehouses.warehouse')),
                ('warehouse_raw_materials', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='raw_warehouse', to='warehouses.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderItemRawMat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField(default=0)),
                ('qty_in', models.CharField(choices=[('0', 'Units'), ('1', 'Packages'), ('2', 'Pallets')], default='0', max_length=10)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='raw_materials', to='products.product')),
                ('work_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='raw_mat_work_order', to='invoices.workorder')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderItemProduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField(default=0)),
                ('qty_in', models.CharField(choices=[('0', 'Units'), ('1', 'Packages'), ('2', 'Pallets')], default='0', max_length=10)),
                ('enviroment_tax_on_workorder', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production', to='products.product')),
                ('work_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prod_work_order', to='invoices.workorder')),
            ],
        ),
        migrations.CreateModel(
            name='TransferOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_in_units', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_with_to', to='products.product')),
                ('to_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_transfer_order_from', to='invoices.transferorder')),
            ],
        ),
        migrations.CreateModel(
            name='RetailSaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('retailitem_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6)),
                ('btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('retailitem_total_with_btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
                ('retail_sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retailitems', to='invoices.retailsale')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField(default=0)),
                ('qty_in', models.CharField(choices=[('0', 'Units'), ('1', 'Packages'), ('2', 'Pallets')], default='0', max_length=10)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('lineitem_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6)),
                ('btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('lineitem_total_with_btw', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lineitems', to='invoices.invoice')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
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
