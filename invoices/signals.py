from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from datetime import *
from django.utils import timezone
from datetime import timedelta, date
import datetime
from dateutil.relativedelta import *

from products.models import HandlingUnit, HandlingUnitMovement
from warehouses.models import Warehouse

from .models import (
    WorkOrder,
    WorkOrderItemProduction,
    WorkOrderItemRawMat,
    Invoice,
    InvoiceItem,
    TransferOrder,
    TransferOrderItem,
    RetailSale,
    RetailSaleItem,
    ConstructionInvoice,
    ConstructionInvoiceItem,
    ConstructionInvoiceLabourCosts,
)
from companies.models import Company

# Custom Imports
from home.handling_unit_operations import create_HU, create_HU_Movement


# Workorders
@receiver(post_save, sender=WorkOrder)
def create_wo_on_save(sender, instance, **kwargs):
    """
    Create Work order number
    """
    if instance.work_order_number == "WO00001":
        workorder_count = WorkOrder.objects.filter(
            company=instance.company).count()
        invoice_prefix = instance.company.invoice_prefix
        instance.work_order_number = (
            invoice_prefix + "WO" + str(workorder_count).zfill(5))
        instance.save()


@receiver(post_save, sender=WorkOrderItemProduction)
def update_on_save_wo_tax(sender, instance, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.work_order.update_tax_wo_total()


@receiver(post_save, sender=WorkOrderItemProduction)
def create_new_hu_on_work_order_save(
        sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    if created:
        if instance.qty_in == "0":
            qty_units = "0"
        else:
            qty_units = "1"
        qty = instance.qty

        # Creates New HU and returns it
        hu_made = create_HU(
            instance.work_order.company,
            instance.work_order.company,
            instance.work_order.company,
            instance.work_order.warehouse_production,
            instance.product,
            qty,
            qty_units,
            instance.work_order.work_order_number,
            instance.work_order.date,
        )
        # Creates New HU Movement
        create_HU_Movement(
            "-",  # Used as dummy variable, needed for function to hadle 'from HU' movements
            hu_made,
            "-",  # Used as dummy variable, needed for function to hadle 'to HU' movements
            instance.work_order.date,
            instance.work_order.work_order_number,
            "Production",
            instance.work_order.company.display_name,
            "-",
            hu_made.hu,
            qty,
        )


@receiver(post_save, sender=WorkOrderItemRawMat)
def grab_items_from_hu_on_work_order_save(
        sender, instance, created, **kwargs):
    """
    Takes products from existing HU to fullfill work order
    """
    if created:
        if instance.qty_in == "0":
            print("Requested " + str(instance.qty) + " units")
            units_to_use = instance.qty
            print(f"Units to use " + str(units_to_use) + "")
            while units_to_use > 0:
                print(f"Units to use (" + str(units_to_use) + ") are > than 0")
                try:
                    print(f"Try to find HU with units")
                    hu_with_product = HandlingUnit.objects.filter(
                        company=instance.work_order.company,
                        location=instance.work_order.warehouse_raw_materials,
                        product=instance.product,
                        qty_units='0',
                        active=True
                        ).order_by('release_date')[0]
                    print(f"Found: ")
                    print(hu_with_product.hu)
                    print(f"With " + str(hu_with_product.qty) + " on it")

                    if hu_with_product.qty > units_to_use:
                        print("Writing off from existing HU as required qty is less than qty on palet and leaving reminder in palet")
                        hu_with_product.qty = hu_with_product.qty - units_to_use
                        hu_with_product.save()
                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.work_order.date,
                            doc_nr=instance.work_order.work_order_number,
                            from_location=instance.work_order.company.display_name,
                            to_location="Production",
                            from_hu=hu_with_product.hu,
                            to_hu="-",
                            qty=instance.qty,
                        )
                        units_to_use = 0

                    elif hu_with_product.qty == units_to_use:
                        print("Writing off all HU as required qty is equal to qty on palet " + hu_with_product.hu)
                        hu_with_product.qty = hu_with_product.qty - units_to_use
                        hu_with_product.active = False
                        hu_with_product.save()
                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.work_order.date,
                            doc_nr=instance.work_order.work_order_number,
                            from_location=instance.work_order.company.display_name,
                            to_location="Production",
                            from_hu=hu_with_product.hu,
                            to_hu="-",
                            qty=instance.qty,
                        )
                        units_to_use = 0

                    else:
                        print("Writing off all HU as required qty is more than qty on palet and returning leftover value")
                        leftover = units_to_use - hu_with_product.qty
                        print(f"Leftover is " + str(leftover) + " as units to use(" + str(units_to_use) + ") is larger than units on palet (" + str(hu_with_product.qty) + " with number " + hu_with_product.hu)
                        units_from_current_hu = units_to_use - leftover
                        hu_with_product.qty = 0
                        hu_with_product.active = False
                        hu_with_product.save()
                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.work_order.date,
                            doc_nr=instance.work_order.work_order_number,
                            from_location=instance.work_order.company.display_name,
                            to_location="Production",
                            from_hu=hu_with_product.hu,
                            to_hu="-",
                            qty=units_from_current_hu,
                        )
                        units_to_use = leftover

                except IndexError:
                    print("No Units found, unpacking Packages")
                    try:
                        hu_with_product = HandlingUnit.objects.filter(
                            company=instance.work_order.company,
                            location=instance.work_order.warehouse_raw_materials,
                            product=instance.product,
                            qty_units='1',
                            active=True
                            ).order_by('release_date')[0]
                        print(f"Found package with HU " + hu_with_product.hu + ", checking qty...")
                        if hu_with_product.qty == 1:
                            print("Quantity on palet is one package")
                            hu_with_product.qty = hu_with_product.qty - 1
                            hu_with_product.active = False
                            hu_with_product.save()
                        else:
                            print("Quantity on palet is more than one package")
                            hu_with_product.qty = hu_with_product.qty - 1
                            hu_with_product.save()
                            print(f"Removing one package and leaving " + str(hu_with_product.qty) + " packages on palet")
                        HandlingUnit.objects.create(
                            manufacturer=hu_with_product.manufacturer,
                            hu_issued_by=instance.work_order.company,
                            company=instance.work_order.company,
                            location=instance.work_order.warehouse_production,
                            product=instance.product,
                            qty=instance.product.units_per_package,
                            qty_units="0",
                            batch_nr=hu_with_product.batch_nr,
                            release_date=hu_with_product.release_date,
                        )
                        print("Created new HU with one package on it, splited in units to procede")
                        hu_made = HandlingUnit.objects.filter(
                            manufacturer=hu_with_product.manufacturer,
                            hu_issued_by=instance.work_order.company,
                            company=instance.work_order.company,
                            location=instance.work_order.warehouse_production,
                            product=instance.product,
                            qty=instance.product.units_per_package,
                            qty_units="0",
                            batch_nr=hu_with_product.batch_nr,
                            release_date=hu_with_product.release_date,
                        ).last()
                        print(f"Created new HU " + hu_made.hu + " from " + hu_with_product.hu)
                        HandlingUnitMovement.objects.create(
                            hu=hu_made,
                            date=instance.work_order.date,
                            doc_nr=instance.work_order.work_order_number,
                            from_location=instance.work_order.company.display_name,
                            to_location=instance.work_order.company.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_made.hu,
                            qty=instance.product.units_per_package,
                        )
                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.work_order.date,
                            doc_nr=instance.work_order.work_order_number,
                            from_location=instance.work_order.company.display_name,
                            to_location=instance.work_order.company.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_made.hu,
                            qty=instance.product.units_per_package,
                        )

                    except IndexError:
                        print("No product Available")
                        break

        else:
            print(f"Requested " + str(instance.qty) + " packages")
            packages_to_use = instance.qty
            while packages_to_use > 0:
                hu_with_product = HandlingUnit.objects.filter(
                    company=instance.work_order.company,
                    location=instance.work_order.warehouse_raw_materials,
                    product=instance.product,
                    qty_units='1',
                    active=True
                    ).order_by('release_date')[0]

                if hu_with_product.qty > packages_to_use:
                    hu_with_product.qty = hu_with_product.qty - instance.qty
                    hu_with_product.save()
                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.work_order.date,
                        doc_nr=instance.work_order.work_order_number,
                        from_location=instance.work_order.company.display_name,
                        to_location="Production",
                        from_hu=hu_with_product.hu,
                        to_hu="-",
                        qty=instance.qty,
                    )
                    packages_to_use = 0

                elif hu_with_product.qty == packages_to_use:
                    hu_with_product.qty = hu_with_product.qty - instance.qty
                    hu_with_product.active = False
                    hu_with_product.save()
                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.work_order.date,
                        doc_nr=instance.work_order.work_order_number,
                        from_location=instance.work_order.company.display_name,
                        to_location="Production",
                        from_hu=hu_with_product.hu,
                        to_hu="-",
                        qty=instance.qty,
                    )
                    packages_to_use = 0

                else:
                    leftover = packages_to_use - hu_with_product.qty
                    packages_from_current_hu = packages_to_use - leftover
                    hu_with_product.qty = 0
                    hu_with_product.active = False
                    hu_with_product.save()
                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.work_order.date,
                        doc_nr=instance.work_order.work_order_number,
                        from_location=instance.work_order.company.display_name,
                        to_location="Production",
                        from_hu=hu_with_product.hu,
                        to_hu="-",
                        qty=packages_from_current_hu,
                    )
                    packages_to_use = leftover


# General Invoices
@receiver(post_save, sender=Invoice)
def create_on_save(sender, instance, created, **kwargs):
    """
    Create Invoice number
    """
    if instance.invoice_number == "AA00001":
        invoice_count = Invoice.objects.filter(
            suplier=instance.suplier).count()
        invoice_prefix = instance.suplier.invoice_prefix
        instance.invoice_number = invoice_prefix + str(invoice_count).zfill(5)
        instance.payment_term = instance.date + timedelta(days=int(instance.payment_term_options))
        instance.save()


@receiver(post_save, sender=InvoiceItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.invoice.update_invoice_total()


@receiver(post_delete, sender=InvoiceItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.invoice.update_invoice_total()


@receiver(post_save, sender=InvoiceItem)
def grab_items_from_hu_on_invoice_save(
        sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    if created:
        if instance.qty_in == "0":
            units_to_use = instance.qty
            while units_to_use > 0:
                try:
                    hu_with_product = HandlingUnit.objects.filter(
                        company=instance.invoice.suplier,
                        location=instance.invoice.suplier_warehouse,
                        product=instance.product,
                        qty_units='0',
                        active=True
                        ).order_by('release_date')[0]
                    if hu_with_product.qty > instance.qty:
                        hu_with_product.qty = hu_with_product.qty - instance.qty
                        hu_with_product.save()

                        HandlingUnit.objects.create(
                            manufacturer=hu_with_product.manufacturer,
                            hu_issued_by=instance.invoice.suplier,
                            company=instance.invoice.suplier,
                            location=instance.invoice.suplier_warehouse,
                            product=instance.product,
                            qty=instance.qty,
                            qty_units="0",
                            batch_nr=hu_with_product.batch_nr,
                            release_date=hu_with_product.release_date,
                        )

                        hu_made = HandlingUnit.objects.filter(
                            manufacturer=hu_with_product.manufacturer,
                            hu_issued_by=instance.invoice.suplier,
                            company=instance.invoice.suplier,
                            location=instance.invoice.suplier_warehouse,
                            product=instance.product,
                            qty=instance.qty,
                            qty_units="0",
                            batch_nr=hu_with_product.batch_nr,
                            release_date=hu_with_product.release_date,
                        ).last()

                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.suplier.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_made,
                            qty=instance.qty,
                        )

                        HandlingUnitMovement.objects.create(
                            hu=hu_made,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.suplier.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_made,
                            qty=instance.qty,
                        )

                        hu_made.company = instance.invoice.customer
                        hu_made.location = instance.invoice.customer_warehouse
                        hu_made.save()

                        HandlingUnitMovement.objects.create(
                            hu=hu_made,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.customer.display_name,
                            from_hu=hu_made,
                            to_hu=hu_made,
                            qty=instance.qty,
                        )

                        units_to_use = 0

                    elif hu_with_product.qty == instance.qty:
                        hu_with_product.company = instance.invoice.customer
                        hu_with_product.location = instance.invoice.customer_warehouse
                        hu_with_product.save()
                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.customer.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_with_product.hu,
                            qty=instance.qty,
                        )
                        units_to_use = 0

                    else:
                        leftover = units_to_use - hu_with_product.qty
                        hu_with_product.company = instance.invoice.customer
                        hu_with_product.location = instance.invoice.customer_warehouse
                        hu_with_product.save()
                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.customer.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_with_product.hu,
                            qty=instance.qty,
                        )
                        units_to_use = leftover
                except IndexError:
                    try:
                        hu_with_product = HandlingUnit.objects.filter(
                            company=instance.invoice.suplier,
                            location=instance.invoice.suplier_warehouse,
                            product=instance.product,
                            qty_units='1',
                            active=True
                        ).order_by('release_date')[0]

                        if hu_with_product.qty == 1:
                            hu_with_product.qty = hu_with_product.qty - 1
                            hu_with_product.active = False
                            hu_with_product.save()
                        else:
                            hu_with_product.qty = hu_with_product.qty - 1
                            hu_with_product.save()

                        HandlingUnit.objects.create(
                            manufacturer=hu_with_product.manufacturer,
                            hu_issued_by=instance.invoice.suplier,
                            company=instance.invoice.suplier,
                            location=instance.invoice.suplier_warehouse,
                            product=instance.product,
                            qty=instance.product.units_per_package,
                            qty_units="0",
                            batch_nr=hu_with_product.batch_nr,
                            release_date=hu_with_product.release_date,
                        )
                        hu_made = HandlingUnit.objects.filter(
                            manufacturer=hu_with_product.manufacturer,
                            hu_issued_by=instance.invoice.suplier,
                            company=instance.invoice.suplier,
                            location=instance.invoice.suplier_warehouse,
                            product=instance.product,
                            qty=instance.product.units_per_package,
                            qty_units="0",
                            batch_nr=hu_with_product.batch_nr,
                            release_date=hu_with_product.release_date,
                        ).last()

                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.suplier.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_made.hu,
                            qty=instance.product.units_per_package,
                        )

                        HandlingUnitMovement.objects.create(
                            hu=hu_made,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.suplier.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_made.hu,
                            qty=instance.product.units_per_package,
                        )

                    except IndexError:
                        print("Index Error")
                        break

        else:
            packages_to_use = instance.qty
            while packages_to_use > 0:
                hu_with_product = HandlingUnit.objects.filter(
                    company=instance.invoice.suplier,
                    location=instance.invoice.suplier_warehouse,
                    product=instance.product,
                    qty_units='1',
                    active=True
                ).order_by('release_date')[0]
                if hu_with_product.qty > instance.qty:
                    hu_with_product.qty = hu_with_product.qty - instance.qty
                    hu_with_product.save()

                    HandlingUnit.objects.create(
                        manufacturer=hu_with_product.manufacturer,
                        hu_issued_by=instance.invoice.suplier,
                        company=instance.invoice.suplier,
                        location=instance.invoice.suplier_warehouse,
                        product=instance.product,
                        qty=instance.qty,
                        qty_units="1",
                        batch_nr=hu_with_product.batch_nr,
                        release_date=hu_with_product.release_date,
                    )

                    hu_made = HandlingUnit.objects.filter(
                        manufacturer=hu_with_product.manufacturer,
                        hu_issued_by=instance.invoice.suplier,
                        company=instance.invoice.suplier,
                        location=instance.invoice.suplier_warehouse,
                        product=instance.product,
                        qty=instance.qty,
                        qty_units="1",
                        batch_nr=hu_with_product.batch_nr,
                        release_date=hu_with_product.release_date,
                    ).last()

                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.invoice.date,
                        doc_nr=instance.invoice.invoice_number,
                        from_location=instance.invoice.suplier.display_name,
                        to_location=instance.invoice.suplier.display_name,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_made,
                        qty=instance.qty,
                    )

                    HandlingUnitMovement.objects.create(
                            hu=hu_made,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.suplier.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_made,
                            qty=instance.qty,
                        )

                    hu_made.company = instance.invoice.customer
                    hu_made.location = instance.invoice.customer_warehouse
                    hu_made.save()

                    HandlingUnitMovement.objects.create(
                            hu=hu_made,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.customer.display_name,
                            from_hu=hu_made,
                            to_hu=hu_made,
                            qty=instance.qty,
                        )

                    packages_to_use = 0

                elif hu_with_product.qty == instance.qty:
                    hu_with_product.company = instance.invoice.customer
                    hu_with_product.location = instance.invoice.customer_warehouse
                    hu_with_product.save()
                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.invoice.date,
                        doc_nr=instance.invoice.invoice_number,
                        from_location=instance.invoice.suplier.display_name,
                        to_location=instance.invoice.customer.display_name,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_with_product.hu,
                        qty=instance.qty,
                    )
                    packages_to_use = 0

                else:
                    leftover = packages_to_use - hu_with_product.qty
                    hu_with_product.company = instance.invoice.customer
                    hu_with_product.location = instance.invoice.customer_warehouse
                    hu_with_product.save()
                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.invoice.date,
                        doc_nr=instance.invoice.invoice_number,
                        from_location=instance.invoice.suplier.display_name,
                        to_location=instance.invoice.customer.display_name,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_with_product.hu,
                        qty=instance.qty,
                    )
                    packages_to_use = leftover


# Transfer Orders
@receiver(post_save, sender=TransferOrder)
def create_to_on_save(sender, instance, **kwargs):
    """
    Create Transfer Order (TO) number
    """
    if instance.to_number == "TO00001":
        to_count = TransferOrder.objects.filter(
            company=instance.company).count()
        invoice_prefix = instance.company.invoice_prefix
        instance.to_number = invoice_prefix + "TO" + str(to_count).zfill(5)
        instance.save()


@receiver(post_save, sender=TransferOrderItem)
def grab_items_from_hu_on_transfer_order_save(
        sender, instance, created, **kwargs):
    """
    Create HU movement
    """
    if created:
        units_to_use = instance.quantity_in_units
        while units_to_use > 0:
            try:
                hu_with_product = HandlingUnit.objects.filter(
                    company=instance.to_number.company,
                    location=instance.to_number.warehouse_from,
                    product=instance.product,
                    qty_units='0',
                    active=True
                    ).order_by('release_date')[0]
                if hu_with_product.qty > instance.quantity_in_units:
                    hu_with_product.qty = hu_with_product.qty - instance.quantity_in_units
                    hu_with_product.save()

                    HandlingUnit.objects.create(
                        manufacturer=hu_with_product.manufacturer,
                        hu_issued_by=instance.to_number.company,
                        company=instance.to_number.company,
                        location=instance.to_number.warehouse_from,
                        product=instance.product,
                        qty=instance.quantity_in_units,
                        qty_units="0",
                        batch_nr=hu_with_product.batch_nr,
                        release_date=hu_with_product.release_date,
                    )

                    hu_made = HandlingUnit.objects.filter(
                        manufacturer=hu_with_product.manufacturer,
                        hu_issued_by=instance.to_number.company,
                        company=instance.to_number.company,
                        location=instance.to_number.warehouse_from,
                        product=instance.product,
                        qty=instance.quantity_in_units,
                        qty_units="0",
                        batch_nr=hu_with_product.batch_nr,
                        release_date=hu_with_product.release_date,
                    ).last()

                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.to_number.date,
                        doc_nr=instance.to_number.to_number,
                        from_location=instance.to_number.warehouse_from.display_name,
                        to_location=instance.to_number.warehouse_from.display_name,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_made,
                        qty=instance.quantity_in_units,
                        )

                    HandlingUnitMovement.objects.create(
                        hu=hu_made,
                        date=instance.to_number.date,
                        doc_nr=instance.to_number.to_number,
                        from_location=instance.to_number.warehouse_from.display_name,
                        to_location=instance.to_number.warehouse_from.display_name,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_made,
                        qty=instance.quantity_in_units,
                    )

                    hu_made.location = instance.to_number.warehouse_to
                    hu_made.active = False
                    hu_made.save()

                    HandlingUnitMovement.objects.create(
                        hu=hu_made,
                        date=instance.to_number.date,
                        doc_nr=instance.to_number.to_number,
                        from_location=instance.to_number.warehouse_from.display_name,
                        to_location=instance.to_number.warehouse_to.display_name,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_made,
                        qty=instance.quantity_in_units,
                    )

                    units_to_use = 0

                elif hu_with_product.qty == instance.quantity_in_units:
                    hu_with_product.qty = hu_with_product.qty - instance.quantity_in_units

                    hu_with_product.location = instance.to_number.warehouse_to
                    hu_with_product.active = False
                    hu_with_product.save()

                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.to_number.date,
                        doc_nr=instance.to_number.to_number,
                        from_location=instance.to_number.warehouse_from.display_name,
                        to_location=instance.to_number.warehouse_to.display_name,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_with_product.hu,
                        qty=instance.quantity_in_units,
                    )

                    units_to_use = 0

                else:
                    leftover = units_to_use - hu_with_product.qty
                    units_from_current_hu = units_to_use - leftover

                    hu_with_product.location = instance.to_number.warehouse_to
                    hu_with_product.active = False
                    hu_with_product.save()

                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.to_number.date,
                        doc_nr=instance.to_number.to_number,
                        from_location=instance.to_number.warehouse_from.display_name,
                        to_location=instance.to_number.warehouse_to.display_name,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_with_product.hu,
                        qty=instance.quantity_in_units,
                    )

                    units_to_use = leftover
            except IndexError:
                hu_with_product = HandlingUnit.objects.filter(
                    company=instance.to_number.company,
                    location=instance.to_number.warehouse_from,
                    product=instance.product,
                    qty_units='1',
                    active=True
                    ).order_by('release_date')[0]

                if hu_with_product.qty == 1:
                    hu_with_product.qty = hu_with_product.qty - 1
                    hu_with_product.active = False
                    hu_with_product.save()
                else:
                    hu_with_product.qty = hu_with_product.qty - 1
                    hu_with_product.save()

                HandlingUnit.objects.create(
                    manufacturer=hu_with_product.manufacturer,
                    hu_issued_by=instance.to_number.company,
                    company=instance.to_number.company,
                    location=instance.to_number.warehouse_from,
                    product=instance.product,
                    qty=instance.quantity_in_units,
                    qty_units="0",
                    batch_nr=hu_with_product.batch_nr,
                    release_date=hu_with_product.release_date,
                )

                hu_made = HandlingUnit.objects.filter(
                    manufacturer=hu_with_product.manufacturer,
                    hu_issued_by=instance.to_number.company,
                    company=instance.to_number.company,
                    location=instance.to_number.warehouse_from,
                    product=instance.product,
                    qty=instance.quantity_in_units,
                    qty_units="0",
                    batch_nr=hu_with_product.batch_nr,
                    release_date=hu_with_product.release_date,
                ).last()

                HandlingUnitMovement.objects.create(
                    hu=hu_with_product,
                    date=instance.to_number.date,
                    doc_nr=instance.to_number.to_number,
                    from_location=instance.to_number.warehouse_from.display_name,
                    to_location=instance.to_number.warehouse_from.display_name,
                    from_hu=hu_with_product.hu,
                    to_hu=hu_made,
                    qty=instance.quantity_in_units,
                )

                HandlingUnitMovement.objects.create(
                    hu=hu_made,
                    date=instance.to_number.date,
                    doc_nr=instance.to_number.to_number,
                    from_location=instance.to_number.warehouse_from.display_name,
                    to_location=instance.to_number.warehouse_from.display_name,
                    from_hu=hu_with_product.hu,
                    to_hu=hu_made,
                    qty=instance.quantity_in_units,
                )


# Retail Sales
@receiver(post_save, sender=RetailSale)
def create_on_save(sender, instance, created, **kwargs):
    """
    Create Invoice number
    """
    if instance.retail_sale_number == "RT1":
        retail_sale_count = RetailSale.objects.filter(
            retailer=instance.retailer).count()
        invoice_prefix = instance.retailer.invoice_prefix
        instance.retail_sale_number = "RT" + invoice_prefix + str(
            retail_sale_count).zfill(8)
        instance.save()


@receiver(post_save, sender=RetailSaleItem)
def update_retail_sale_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.retail_sale.update_retail_sale_total()


@receiver(post_save, sender=RetailSaleItem)
def grab_items_from_hu_on_retail_sale_save(
        sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    if created:
        units_to_use = instance.quantity

        try:

            oldest_hu_units = HandlingUnit.objects.filter(
                company=instance.retail_sale.retailer,
                location=instance.retail_sale.retailer_warehouse,
                product=instance.product,
                qty_units='0',
                active=True
                ).order_by('release_date')[0]
        except IndexError:
            oldest_hu_units = 0

        try:
            oldest_hu_packages = HandlingUnit.objects.filter(
                company=instance.retail_sale.retailer,
                location=instance.retail_sale.retailer_warehouse,
                product=instance.product,
                qty_units='1',
                active=True
                ).order_by('release_date')[0]
        except IndexError:
            oldest_hu_packages = 0

        if oldest_hu_units != 0 and oldest_hu_packages != 0:
            if oldest_hu_units.release_date > oldest_hu_packages.release_date:
                if oldest_hu_packages.qty == 1:
                    oldest_hu_packages.qty_units = "0"
                    oldest_hu_packages.qty = instance.product.units_per_package
                    oldest_hu_packages.save()
        elif oldest_hu_units == 0:
            if oldest_hu_packages.qty == 1:
                oldest_hu_packages.qty_units = "0"
                oldest_hu_packages.qty = instance.product.units_per_package
                oldest_hu_packages.save()
            else:
                oldest_hu_packages.qty = oldest_hu_packages.qty_units - 1
                oldest_hu_packages.save()

                HandlingUnit.objects.create(
                    manufacturer=oldest_hu_packages.manufacturer,
                    hu_issued_by=instance.retail_sale.retailer,
                    company=instance.retail_sale.retailer,
                    location=instance.retail_sale.retailer_warehouse,
                    product=instance.product,
                    qty=instance.product.units_per_package,
                    qty_units="0",
                    batch_nr=oldest_hu_packages.batch_nr,
                    release_date=oldest_hu_packages.release_date,
                )

                hu_made = HandlingUnit.objects.filter(
                    manufacturer=oldest_hu_packages.manufacturer,
                    hu_issued_by=instance.retail_sale.retailer,
                    company=instance.retail_sale.retailer,
                    location=instance.retail_sale.retailer_warehouse,
                    product=instance.product,
                    qty=instance.product.units_per_package,
                    qty_units="0",
                    batch_nr=oldest_hu_packages.batch_nr,
                    release_date=oldest_hu_packages.release_date,
                ).last()

                HandlingUnitMovement.objects.create(
                    hu=oldest_hu_packages,
                    date=instance.retail_sale.date,
                    doc_nr=instance.retail_sale.retail_sale_number,
                    from_location=instance.retail_sale.retailer_warehouse,
                    to_location=instance.retail_sale.retailer_warehouse,
                    from_hu=oldest_hu_packages.hu,
                    to_hu=hu_made,
                    qty=units_to_use,
                    )

                HandlingUnitMovement.objects.create(
                    hu=hu_made,
                    date=instance.retail_sale.date,
                    doc_nr=instance.retail_sale.retail_sale_number,
                    from_location=instance.retail_sale.retailer_warehouse,
                    to_location=instance.retail_sale.retailer_warehouse,
                    from_hu=oldest_hu_packages.hu,
                    to_hu=hu_made,
                    qty=units_to_use,
                    )

        while units_to_use > 0:
            hu_with_product = HandlingUnit.objects.filter(
                company=instance.retail_sale.retailer,
                location=instance.retail_sale.retailer_warehouse,
                product=instance.product,
                qty_units='0',
                active=True
                ).order_by('release_date')[0]
            if hu_with_product.qty > units_to_use:
                hu_with_product.qty = hu_with_product.qty - instance.quantity
                hu_with_product.save()

                HandlingUnit.objects.create(
                    manufacturer=hu_with_product.manufacturer,
                    hu_issued_by=instance.retail_sale.retailer,
                    company=instance.retail_sale.retailer,
                    location=instance.retail_sale.retailer_warehouse,
                    product=instance.product,
                    qty=instance.quantity,
                    qty_units="0",
                    batch_nr=hu_with_product.batch_nr,
                    release_date=hu_with_product.release_date,
                )

                hu_made = HandlingUnit.objects.filter(
                    manufacturer=hu_with_product.manufacturer,
                    hu_issued_by=instance.retail_sale.retailer,
                    company=instance.retail_sale.retailer,
                    location=instance.retail_sale.retailer_warehouse,
                    product=instance.product,
                    qty=instance.quantity,
                    qty_units="0",
                    batch_nr=hu_with_product.batch_nr,
                    release_date=hu_with_product.release_date,
                ).last()

                HandlingUnitMovement.objects.create(
                    hu=hu_with_product,
                    date=instance.retail_sale.date,
                    doc_nr=instance.retail_sale.retail_sale_number,
                    from_location=instance.retail_sale.retailer_warehouse,
                    to_location=instance.retail_sale.retailer_warehouse,
                    from_hu=hu_with_product.hu,
                    to_hu=hu_made,
                    qty=units_to_use,
                    )

                HandlingUnitMovement.objects.create(
                    hu=hu_made,
                    date=instance.retail_sale.date,
                    doc_nr=instance.retail_sale.retail_sale_number,
                    from_location=instance.retail_sale.retailer_warehouse,
                    to_location=instance.retail_sale.retailer_warehouse,
                    from_hu=hu_with_product.hu,
                    to_hu=hu_made,
                    qty=units_to_use,
                )

                hu_made.active = False
                hu_made.save()

                HandlingUnitMovement.objects.create(
                    hu=hu_made,
                    date=instance.retail_sale.date,
                    doc_nr=instance.retail_sale.retail_sale_number,
                    from_location=instance.retail_sale.retailer_warehouse,
                    to_location="Sales",
                    from_hu=hu_with_product.hu,
                    to_hu="-",
                    qty=units_to_use,
                )

                units_to_use = 0

            elif hu_with_product.qty == units_to_use:
                hu_with_product.qty = hu_with_product.qty - units_to_use

                hu_with_product.active = False
                hu_with_product.save()

                HandlingUnitMovement.objects.create(
                    hu=hu_with_product,
                    date=instance.retail_sale.date,
                    doc_nr=instance.retail_sale.retail_sale_number,
                    from_location=instance.retail_sale.retailer_warehouse,
                    to_location="Sales",
                    from_hu=hu_with_product.hu,
                    to_hu="-",
                    qty=units_to_use,
                )

                units_to_use = 0

            else:
                leftover = units_to_use - hu_with_product.qty
                units_from_current_hu = units_to_use - leftover

                hu_with_product.active = False
                hu_with_product.save()

                HandlingUnitMovement.objects.create(
                    hu=hu_with_product,
                    date=instance.retail_sale.date,
                    doc_nr=instance.retail_sale.retail_sale_number,
                    from_location=instance.retail_sale.retailer_warehouse,
                    to_location="Sales",
                    from_hu=hu_with_product.hu,
                    to_hu="-",
                    qty=units_to_use,
                )

                units_to_use = leftover


# Construction Invoice
@receiver(post_save, sender=ConstructionInvoice)
def create_on_save(sender, instance, created, **kwargs):
    """
    Create Invoice number
    """
    if instance.c_invoice_number == "C1":
        c_invoice_count = ConstructionInvoice.objects.filter(constructor=instance.constructor).count()
        invoice_prefix = instance.constructor.invoice_prefix
        instance.c_invoice_number = "CI" + invoice_prefix + str(c_invoice_count).zfill(5)
        instance.save()


@receiver(post_save, sender=ConstructionInvoiceItem)
def update_construction_invoice_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.c_invoice.update_c_invoice_total()


@receiver(post_save, sender=ConstructionInvoiceLabourCosts)
def update_construction_invoice_on_save_labour_costs(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.c_invoice.update_c_invoice_total()


@receiver(post_save, sender=ConstructionInvoiceItem)
def grab_items_from_hu_on_construction_invoice_save(
        sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    if created:
        units_to_use = instance.quantity
        while units_to_use > 0:
            try:
                hu_with_product = HandlingUnit.objects.filter(
                    company=instance.c_invoice.constructor,
                    location=instance.c_invoice.constructor_warehouse,
                    product=instance.product,
                    qty_units='0',
                    active=True
                ).order_by('release_date')[0]
                if hu_with_product.qty > units_to_use:
                    hu_with_product.qty = hu_with_product.qty - instance.quantity
                    hu_with_product.save()

                    HandlingUnit.objects.create(
                        manufacturer=hu_with_product.manufacturer,
                        hu_issued_by=instance.c_invoice.constructor,
                        company=instance.c_invoice.constructor,
                        location=instance.c_invoice.constructor_warehouse,
                        product=instance.product,
                        qty=instance.quantity,
                        qty_units="0",
                        batch_nr=hu_with_product.batch_nr,
                        release_date=hu_with_product.release_date,
                    )
                    hu_made = HandlingUnit.objects.filter(
                        manufacturer=hu_with_product.manufacturer,
                        hu_issued_by=instance.c_invoice.constructor,
                        company=instance.c_invoice.constructor,
                        location=instance.c_invoice.constructor_warehouse,
                        product=instance.product,
                        qty=instance.quantity,
                        qty_units="0",
                        batch_nr=hu_with_product.batch_nr,
                        release_date=hu_with_product.release_date,
                    ).last()
                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.c_invoice.date,
                        doc_nr=instance.c_invoice.c_invoice_number,
                        from_location=instance.c_invoice.constructor_warehouse,
                        to_location=instance.c_invoice.constructor_warehouse,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_made,
                        qty=units_to_use,
                    )
                    HandlingUnitMovement.objects.create(
                        hu=hu_made,
                        date=instance.c_invoice.date,
                        doc_nr=instance.c_invoice.c_invoice_number,
                        from_location=instance.c_invoice.constructor_warehouse,
                        to_location=instance.c_invoice.constructor_warehouse,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_made,
                        qty=units_to_use,
                    )

                    hu_made.active = False
                    hu_made.save()

                    HandlingUnitMovement.objects.create(
                        hu=hu_made,
                        date=instance.c_invoice.date,
                        doc_nr=instance.c_invoice.c_invoice_number,
                        from_location=instance.c_invoice.constructor_warehouse,
                        to_location="Construction",
                        from_hu=hu_with_product.hu,
                        to_hu="-",
                        qty=units_to_use,
                    )

                    units_to_use = 0

                elif hu_with_product.qty == units_to_use:
                    hu_with_product.qty = hu_with_product.qty - units_to_use

                    hu_with_product.active = False
                    hu_with_product.save()

                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.c_invoice.date,
                        doc_nr=instance.c_invoice.c_invoice_number,
                        from_location=instance.c_invoice.constructor_warehouse,
                        to_location="Construction",
                        from_hu=hu_with_product.hu,
                        to_hu="-",
                        qty=units_to_use,
                    )

                    units_to_use = 0

                else:
                    leftover = units_to_use - hu_with_product.qty
                    units_from_current_hu = units_to_use - leftover

                    hu_with_product.active = False
                    hu_with_product.save()

                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.c_invoice.date,
                        doc_nr=instance.c_invoice.c_invoice_number,
                        from_location=instance.c_invoice.constructor_warehouse,
                        to_location="Construction",
                        from_hu=hu_with_product.hu,
                        to_hu="-",
                        qty=units_to_use,
                    )

                    units_to_use = leftover
            
            except IndexError:
                try:
                    hu_with_product = HandlingUnit.objects.filter(
                        company=instance.c_invoice.constructor,
                        location=instance.c_invoice.constructor_warehouse,
                        product=instance.product,
                        qty_units='1',
                        active=True
                    ).order_by('release_date')[0]
                    if hu_with_product.qty == 1:
                        print("Quantity on palet is one package")
                        hu_with_product.qty = hu_with_product.qty - 1
                        hu_with_product.active = False
                        hu_with_product.save()
                    else:
                        print("Quantity on palet is more than one package")
                        hu_with_product.qty = hu_with_product.qty - 1
                        hu_with_product.save()
                        print(f"Removing one package and leaving " + hu_with_product.qty + " packages on palet")
                    HandlingUnit.objects.create(
                        manufacturer=hu_with_product.manufacturer,
                        hu_issued_by=instance.c_invoice.constructor,
                        company=instance.c_invoice.constructor,
                        location=instance.c_invoice.constructor_warehouse,
                        product=instance.product,
                        qty=instance.product.units_per_package,
                        qty_units="0",
                        batch_nr=hu_with_product.batch_nr,
                        release_date=hu_with_product.release_date,
                    )
                    print("Created new HU with one package on it, splited in units to procede")
                    hu_made = HandlingUnit.objects.filter(
                        manufacturer=hu_with_product.manufacturer,
                        hu_issued_by=instance.c_invoice.constructor,
                        company=instance.c_invoice.constructor,
                        location=instance.c_invoice.constructor_warehouse,
                        product=instance.product,
                        qty=instance.product.units_per_package,
                        qty_units="0",
                        batch_nr=hu_with_product.batch_nr,
                        release_date=hu_with_product.release_date,
                    ).last()
                    print(f"Created new HU " + hu_made.hu + " from " + hu_with_product.hu)
                    HandlingUnitMovement.objects.create(
                        hu=hu_made,
                        date=instance.work_order.date,
                        doc_nr=instance.work_order.work_order_number,
                        from_location=instance.work_order.company.display_name,
                        to_location=instance.work_order.company.display_name,
                        from_hu=hu_with_product.hu,
                        to_hu=hu_made.hu,
                        qty=instance.product.units_per_package,
                    )
                except IndexError:
                    print("No product Available")
                    break
