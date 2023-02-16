from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from companies.models import Company
from warehouses.models import Warehouse
from products.models import Product, HandlingUnit


class WorkOrder(models.Model):
    work_order_number = models.CharField(max_length=10, default='WO00001')
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="company_work_order")
    warehouse_raw_materials = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="raw_warehouse")
    warehouse_production = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="production_warehouse")
    date = models.DateField(auto_now_add=False)
    enviroment_tax_on_workorder_total = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return self.work_order_number

    def update_tax_wo_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.enviroment_tax_on_workorder_total = (
            self.prod_work_order.aggregate(
                Sum('enviroment_tax_on_workorder')
                    )['enviroment_tax_on_workorder__sum'] or 0)
        super().save()


class WorkOrderItemRawMat(models.Model):
    work_order = models.ForeignKey(
        WorkOrder, null=False, blank=False,
        on_delete=models.CASCADE, related_name='raw_mat_work_order')
    product = models.ForeignKey(
        Product, null=False, blank=False,
        on_delete=models.CASCADE, related_name='raw_materials')
    quantity_in_units = models.IntegerField(null=False, blank=False, default=0)
    quantity_in_packages = models.IntegerField(null=False, blank=False, default=0)


class WorkOrderItemProduction(models.Model):
    work_order = models.ForeignKey(
        WorkOrder, null=False, blank=False,
        on_delete=models.CASCADE, related_name='prod_work_order')
    product = models.ForeignKey(
        Product, null=False, blank=False,
        on_delete=models.CASCADE, related_name='production')
    quantity_in_single_units = models.IntegerField(null=False, blank=False, default=0)
    quantity_in_units = models.IntegerField(null=False, blank=False, default=0)
    quantity_in_packages = models.IntegerField(null=False, blank=False, default=0)
    enviroment_tax_on_workorder = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.enviroment_tax_on_workorder = (
            self.product.enviroment_tax_amount * self.quantity_in_single_units)
        if self.product.units_per_package > self.quantity_in_single_units:
            self.quantity_in_packages = 0
            self.quantity_in_units = self.quantity_in_single_units
            super().save(*args, **kwargs)
        elif self.quantity_in_single_units % self.product.units_per_package == 0:
            self.quantity_in_packages = self.quantity_in_single_units / self.product.units_per_package
            self.quantity_in_units = 0
            super().save(*args, **kwargs)
        else:
            print("Cannot divide in packages AND units")
            pass
