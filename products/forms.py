from django import forms
from .models import Category, SubCategory, Product


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = [
            'display_name'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'select select-category col-6 add-product-select-field mb-4'

    def clean_display_name(self):
        data = self.cleaned_data.get("display_name")
        print(data)
        if len(data) > 80:
            raise forms.ValidationError("Max characters = 80!")
        elif len(data) < 4:
            raise forms.ValidationError("Min characters = 4!")
        return data


class SubCategoryForm(forms.ModelForm):

    class Meta:
        model = SubCategory
        fields = [
            'category',
            'display_name',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = Category.objects.all()
        display_name_categories = [(c.id, c.get_display_name()) for c in categories]
        self.fields['category'].choices = display_name_categories

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'select select-category col-6 add-product-select-field mb-4'


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'category',
            'subcategory',
            'display_name',
            'name',
            'code',
            'enviroment_tax_class',
            'expiry_end_date_terms',
            'expiry_end_date_cat',
            'units_per_package',
            'packages_per_lay',
            'lay_per_palet',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = Category.objects.all()
        display_name_categories = [(c.id, c.get_display_name()) for c in categories]
        self.fields['category'].choices = display_name_categories

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'select col-6 add-product-select-field mb-4'
