from django import forms
from django.forms import inlineformset_factory

from .models import Invoice, InvoiceItem
from companies.models import Company
from warehouses.models import Warehouse
from products.models import Product




class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            'invoice_number',
            'suplier',
            'customer',
            'suplier_warehouse',
            'customer_warehouse',
            'date',
            'payment_term_options',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        companies = Company.objects.all()
        display_name_companies = [(c.registration_number, c.get_display_name()) for c in companies]
        self.fields['suplier'].choices = display_name_companies
        self.fields['customer'].choices = display_name_companies

        suplier_choices = list(self.fields['suplier'].choices)
        suplier_choices.insert(0, ('', ' - '))
        self.fields['suplier'].choices = suplier_choices

        customer_choices = list(self.fields['customer'].choices)
        customer_choices.insert(0, ('', ' - '))
        self.fields['customer'].choices = customer_choices

        warehouses = Warehouse.objects.filter(internal_warehouse=False)
        display_name_warehouses = [(w.id, w.get_display_name()) for w in warehouses]
        self.fields['suplier_warehouse'].choices = display_name_warehouses
        self.fields['customer_warehouse'].choices = display_name_warehouses

        suplier_warehouse_choices = list(self.fields['suplier_warehouse'].choices)
        suplier_warehouse_choices.insert(0, ('NotSelected', ' - '))
        self.fields['suplier_warehouse'].choices = suplier_warehouse_choices

        customer_warehouse_choices = list(self.fields['customer_warehouse'].choices)
        customer_warehouse_choices.insert(0, ('NotSelected', ' - '))
        self.fields['customer_warehouse'].choices = customer_warehouse_choices

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'select add-product-select-field mb-1'
        self.fields['invoice_number'].widget.attrs['readonly'] = True
        self.fields['invoice_number'].widget.attrs['class'] = 'not-allowed add-product-select-field mb-1'


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = (
            'product',
            'qty',
            'qty_in',
            'price',
            'lineitem_total',
            'btw',
            'lineitem_total_with_btw',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        products = Product.objects.all()
        display_name_products = [(p.id, p.get_display_name()) for p in products]
        self.fields['product'].choices = display_name_products

        products_choices = list(self.fields['product'].choices)
        products_choices.insert(0, ('NotSelected', ' - '))
        self.fields['product'].choices = products_choices


InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=1)
