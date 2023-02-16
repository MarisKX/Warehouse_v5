from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from products.models import HandlingUnit, HandlingUnitMovement
from warehouses.models import Warehouse

from .models import (
    WorkOrder,
    WorkOrderItemProduction,
    WorkOrderItemRawMat,
)


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
                location=instance.work_order.warehouse_production,
                product=instance.product,
                qty=qty,
                qty_units=qty_units,
                batch_nr=instance.work_order.work_order_number,
                release_date=instance.work_order.date,
            )
        hu_made = HandlingUnit.objects.filter(
            manufacturer=instance.work_order.company,
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
                to_location="Warehouse",
                from_hu="",
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
                        product=instance.product, qty_units='0', active=True).order_by('release_date')[0]
                    if hu_with_product.qty > instance.quantity_in_units:
                        hu_with_product.qty = hu_with_product.qty - instance.quantity_in_units
                        hu_with_product.save()
                        HandlingUnitMovement.objects.create(
                            hu=hu_with_product,
                            date=instance.work_order.date,
                            doc_nr=instance.work_order.work_order_number,
                            from_location="Warehouse",
                            to_location="Production",
                            from_hu=hu_with_product.hu,
                            to_hu="",
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
                            from_location="Warehouse",
                            to_location="Production",
                            from_hu=hu_with_product.hu,
                            to_hu="",
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
                            from_location="Warehouse",
                            to_location="Production",
                            from_hu=hu_with_product.hu,
                            to_hu="",
                            qty=units_from_current_hu,
                        )
                        units_to_use = leftover

                except ObjectDoesNotExist:
                    print("Object Does not exist")
