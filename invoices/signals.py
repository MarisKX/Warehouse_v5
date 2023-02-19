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
    TransferOrderItem
)
from companies.models import Company


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
        if instance.quantity_in_units == 0:
            qty = instance.quantity_in_packages
            qty_units = "1"
        else:
            qty = instance.quantity_in_units
            qty_units = "0"
        HandlingUnit.objects.create(
                manufacturer=instance.work_order.company,
                company=instance.work_order.company,
                location=instance.work_order.warehouse_production,
                product=instance.product,
                qty=qty,
                qty_units=qty_units,
                batch_nr=instance.work_order.work_order_number,
                release_date=instance.work_order.date,
            )
        hu_made = HandlingUnit.objects.filter(
            manufacturer=instance.work_order.company,
            company=instance.work_order.company,
            location=instance.work_order.warehouse_production,
            product=instance.product,
            qty=qty,
            qty_units=qty_units,
            batch_nr=instance.work_order.work_order_number,
            release_date=instance.work_order.date,
            ).last()
        HandlingUnitMovement.objects.create(
                hu=hu_made,
                date=instance.work_order.date,
                doc_nr=instance.work_order.work_order_number,
                from_location="Production",
                to_location=instance.work_order.company.display_name,
                from_hu="-",
                to_hu=hu_made.hu,
                qty=qty,
            )


@receiver(post_save, sender=WorkOrderItemRawMat)
def grab_items_from_hu_on_work_order_save(
        sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    if created:
        if instance.quantity_in_packages == 0:
            units_to_use = instance.quantity_in_units
            while units_to_use > 0:
                try:
                    hu_with_product = HandlingUnit.objects.filter(
                        company=instance.work_order.company,
                        product=instance.product,
                        qty_units='0',
                        active=True
                        ).order_by('release_date')[0]

                    if hu_with_product.qty > instance.quantity_in_units:
                        hu_with_product.qty = hu_with_product.qty - instance.quantity_in_units
                        hu_with_product.save()
                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.work_order.date,
                            doc_nr=instance.work_order.work_order_number,
                            from_location=instance.work_order.company.display_name,
                            to_location="Production",
                            from_hu=hu_with_product.hu,
                            to_hu="-",
                            qty=instance.quantity_in_units,
                        )
                        units_to_use = 0

                    elif hu_with_product.qty == instance.quantity_in_units:
                        hu_with_product.qty = hu_with_product.qty - instance.quantity_in_units
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
                            qty=instance.quantity_in_units,
                        )
                        units_to_use = 0

                    else:
                        leftover = units_to_use - hu_with_product.qty
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
                    try:
                        hu_with_product = HandlingUnit.objects.filter(
                            company=instance.work_order.company,
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
                            manufacturer=instance.work_order.company,
                            company=instance.work_order.company,
                            location=instance.work_order.warehouse_production,
                            product=instance.product,
                            qty=instance.product.units_per_package,
                            qty_units="0",
                            batch_nr=hu_with_product.batch_nr,
                            release_date=hu_with_product.release_date,
                        )
                        hu_made = HandlingUnit.objects.filter(
                            manufacturer=instance.work_order.company,
                            company=instance.work_order.company,
                            location=instance.work_order.warehouse_production,
                            product=instance.product,
                            qty=instance.product.units_per_package,
                            qty_units="0",
                            batch_nr=hu_with_product.batch_nr,
                            release_date=hu_with_product.release_date,
                        ).last()
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
                        break

        else:
            packages_to_use = instance.quantity_in_packages
            while packages_to_use > 0:
                hu_with_product = HandlingUnit.objects.filter(
                    company=instance.work_order.company,
                    product=instance.product,
                    qty_units='1',
                    active=True
                    ).order_by('release_date')[0]
                if hu_with_product.qty > instance.quantity_in_packages:
                    hu_with_product.qty = hu_with_product.qty - instance.quantity_in_packages
                    hu_with_product.save()
                    HandlingUnitMovement.objects.create(
                        hu=hu_with_product,
                        date=instance.work_order.date,
                        doc_nr=instance.work_order.work_order_number,
                        from_location=instance.work_order.company.display_name,
                        to_location="Production",
                        from_hu=hu_with_product.hu,
                        to_hu="-",
                        qty=instance.quantity_in_packages,
                    )
                    packages_to_use = 0

                elif hu_with_product.qty == instance.quantity_in_packages:
                    hu_with_product.qty = hu_with_product.qty - instance.quantity_in_packages
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
                        qty=instance.quantity_in_packages,
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
        if instance.quantity_in_packages == 0:
            units_to_use = instance.quantity_in_units
            while units_to_use > 0:
                try:
                    hu_with_product = HandlingUnit.objects.filter(
                        company=instance.invoice.suplier,
                        location=instance.invoice.suplier_warehouse,
                        product=instance.product,
                        qty_units='0',
                        active=True
                        ).order_by('release_date')[0]
                    if hu_with_product.qty > instance.quantity_in_units:
                        hu_with_product.qty = hu_with_product.qty - instance.quantity_in_units
                        hu_with_product.save()

                        HandlingUnit.objects.create(
                            manufacturer=hu_with_product.manufacturer,
                            company=instance.invoice.suplier,
                            location=instance.invoice.suplier_warehouse,
                            product=instance.product,
                            qty=instance.quantity_in_units,
                            qty_units="0",
                            batch_nr=hu_with_product.batch_nr,
                            release_date=hu_with_product.release_date,
                        )

                        hu_made = HandlingUnit.objects.filter(
                            manufacturer=hu_with_product.manufacturer,
                            company=instance.invoice.suplier,
                            location=instance.invoice.suplier_warehouse,
                            product=instance.product,
                            qty=instance.quantity_in_units,
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
                            qty=instance.quantity_in_units,
                        )

                        HandlingUnitMovement.objects.create(
                            hu=hu_made,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.suplier.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_made,
                            qty=instance.quantity_in_units,
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
                            qty=instance.quantity_in_units,
                        )

                        units_to_use = 0

                    elif hu_with_product.qty == instance.quantity_in_units:
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
                            qty=instance.quantity_in_units,
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
                            qty=instance.quantity_in_units,
                        )
                        units_to_use = leftover
                except IndexError:
                    print("Index Error")
                    break

        else:
            packages_to_use = instance.quantity_in_packages
            while packages_to_use > 0:
                hu_with_product = HandlingUnit.objects.filter(
                    product=instance.product, qty_units='1', active=True).order_by('release_date')[0]
                if hu_with_product.qty > instance.quantity_in_packages:
                    hu_with_product.qty = hu_with_product.qty - instance.quantity_in_packages
                    hu_with_product.save()

                    HandlingUnit.objects.create(
                        manufacturer=hu_with_product.manufacturer,
                        company=instance.invoice.suplier,
                        location=instance.invoice.suplier_warehouse,
                        product=instance.product,
                        qty=instance.quantity_in_packages,
                        qty_units="1",
                        batch_nr=hu_with_product.batch_nr,
                        release_date=hu_with_product.release_date,
                    )

                    hu_made = HandlingUnit.objects.filter(
                        manufacturer=hu_with_product.manufacturer,
                        company=instance.invoice.suplier,
                        location=instance.invoice.suplier_warehouse,
                        product=instance.product,
                        qty=instance.quantity_in_packages,
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
                        qty=instance.quantity_in_packages,
                    )

                    HandlingUnitMovement.objects.create(
                            hu=hu_made,
                            date=instance.invoice.date,
                            doc_nr=instance.invoice.invoice_number,
                            from_location=instance.invoice.suplier.display_name,
                            to_location=instance.invoice.suplier.display_name,
                            from_hu=hu_with_product.hu,
                            to_hu=hu_made,
                            qty=instance.quantity_in_packages,
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
                            qty=instance.quantity_in_packages,
                        )

                    packages_to_use = 0

                elif hu_with_product.qty == instance.quantity_in_packages:
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
                        qty=instance.quantity_in_packages,
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
                        qty=instance.quantity_in_packages,
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
    Update order total on lineitem update/create
    """
    if created:
        units_to_use = instance.quantity_in_units
        while units_to_use > 0:
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
