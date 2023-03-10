# General imports
from django.shortcuts import render, get_object_or_404, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# PDF imports
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.lib.pagesizes import letter, A4

# Additional for barcodes
from reportlab.graphics.barcode import code39, code128, code93
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing

# Model imports
from .models import Product, Category, SubCategory, HandlingUnit, HandlingUnitMovement
from companies.models import Company
from warehouses.models import Warehouse

# Form imports
from .forms import ProductForm, CategoryForm, SubCategoryForm


# All Products view
@login_required
def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all().order_by("display_name")
    all_categories = Category.objects.all()
    all_subcategories = SubCategory.objects.all()

    def is_ajax(request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    if is_ajax(request):
        category = request.GET.get('category')
        if category is not None:
            subcategories = SubCategory.objects.filter(
                category=category).order_by("display_name").values_list('display_name')
            subcategories_id = SubCategory.objects.filter(
                category=category).order_by("display_name").values_list('id')
            return JsonResponse({
                "subcategories_to_return": list(subcategories),
                "subcategories_id_to_return": list(subcategories_id),
                })

    if request.GET:
        if 'category' and 'subcategory' in request.GET:
            query_filter_category = request.GET['category']
            query_filter_subcategory = request.GET['subcategory']
            if query_filter_subcategory != "":
                queries = Q(
                    category_id=query_filter_category) & Q(
                    subcategory_id=query_filter_subcategory)
                products = products.filter(queries)
            else:
                queries = Q(
                    category__id__icontains=query_filter_category)
                products = products.filter(queries)

        if 'category' in request.GET:
            query_filter_category = request.GET['category']
            if query_filter_category != "":
                queries = Q(
                    category__id__icontains=query_filter_category)
                products = products.filter(queries)
            else:
                Product.objects.all().order_by("display_name")

    context = {
        'products': products,
        'all_categories': all_categories,
        'all_subcategories': all_subcategories,
    }

    return render(request, 'products/products.html', context)


# Product Details View
@login_required
def product_details(request, code):
    """ A view to return the product detail page """

    product = get_object_or_404(Product, code=code)

    context = {
        'product': product,
    }

    return render(request, 'products/product_details.html', context)


# Product Details View in PDF
@login_required
def product_details_in_pdf(request, code):
    """ A view to return the product detail page """

    product = get_object_or_404(Product, code=code)

    if product.enviroment_tax_class != "0":
        env_tax_amount = str(product.enviroment_tax_amount)
    else:
        env_tax_amount = "-"

    # Create Bytestream buffer
    buf = io.BytesIO()
    # Create Canvas
    c = canvas.Canvas(buf, pagesize=A4, bottomup=0)
    c.translate(inch, inch)
    c.setStrokeColor("black")
    c.setLineWidth(1)
    c.line(0, 45, 450, 45)
    c.line(0, 130, 450, 130)

    c.setStrokeColor("black")
    c.setLineWidth(1)
    c.line(0, 400, 450, 400)
    c.line(0, 130, 450, 130)

    textobj_reg = c.beginText()
    textobj_reg.setTextOrigin(45, 160)
    textobj_reg.setFont("Helvetica", 14)

    textobj_xl = c.beginText()
    textobj_xl.setTextOrigin(45, 100)
    textobj_xl.setFont("Helvetica", 35)

    textobj_sm = c.beginText()
    textobj_sm.setTextOrigin(310, 120)
    textobj_sm.setFont("Helvetica", 8)
    textobj_sm.setCharSpace(8)

    textobj_calc_names = c.beginText()
    textobj_calc_names.setTextOrigin(45, 450)
    textobj_calc_names.setFont("Helvetica", 14)
    textobj_calc_names.setCharSpace(3)

    textobj_calc_value = c.beginText()
    textobj_calc_value.setTextOrigin(270, 450)
    textobj_calc_value.setFont("Helvetica", 16)
    textobj_calc_value.setCharSpace(3)

    reg_lines = [
        " ",
        "Category:",
        product.category.display_name,
        " ",
        "Subcategory:",
        product.subcategory.display_name,
        " ",
        "Enviroment Tax Class:",
        product.get_enviroment_tax_class_display(),
    ]

    if product.enviroment_tax_class != "0":
        reg_lines.append(" ")
        reg_lines.append("Enviroment Tax:")
        reg_lines.append(env_tax_amount + " Eur")

    lg_lines = [
        " ",
        "Name:",
        product.display_name,
    ]

    calc_lines_name = [
        "Units per package:",
        " ",
        "Packages per palet:",
        " ",
        "Units per palet:",
    ]

    calc_lines_value = [
        str(product.units_per_package),
        " ",
        str(product.packages_per_palet),
        " ",
        str(product.units_per_palet),
    ]

    article = product.code
    barcode = product.code.lower()
    # barcode = "12341570"

    for line in lg_lines:
        textobj_reg.setFont("Helvetica", 24)
        textobj_reg.textLine(line)

    for line in reg_lines:
        textobj_reg.setFont("Helvetica", 14)
        textobj_reg.textLine(line)

    for line in calc_lines_name:
        textobj_calc_names.setFont("Helvetica", 16)
        textobj_calc_names.textLine(line)

    for line in calc_lines_value:
        textobj_calc_value.setFont("Helvetica", 16)
        textobj_calc_value.textLine(line)

    textobj_xl.textLine(article)
    textobj_sm.textLine(barcode)

    # Draw the 39 code
    barcode39Std = code39.Extended39(barcode, barHeight=40, stop=1, checksum=0)

    # barcode128 = code128.Code128(article)

    codes = [barcode39Std,]

    x = 100 * mm
    y = 25 * mm
    x1 = 6.4 * mm

    for code in codes:
        code.drawOn(c, x, y)
        y = y - 15 * mm

    # draw the eanbc8 code
    # barcode_eanbc8 = eanbc.Ean8BarcodeWidget(barcode)
    # bounds = barcode_eanbc8.getBounds()
    # width = bounds[2] - bounds[0]
    # height = bounds[3] - bounds[1]
    # d = Drawing(50, 10)
    # d.add(barcode_eanbc8)
    # renderPDF.draw(d, c, 300, 75)

    c.drawText(textobj_xl)
    c.drawText(textobj_reg)
    c.drawText(textobj_sm)
    c.drawText(textobj_calc_names)
    c.drawText(textobj_calc_value)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=f"" + product.display_name + "_" + product.code.lower() + ".pdf")


# Add New category and/or subcategory
@login_required
def add_category(request):
    """ A view to return the product detail page """

    def is_ajax(request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    add_cat_form = CategoryForm()
    add_subcat_form = SubCategoryForm()

    if request.method == "POST":
        if 'add-category-btn' in request.POST:
            add_cat_form = CategoryForm(request.POST or None)
            if add_cat_form.is_valid():
                obj = add_cat_form.save(commit=False)
                obj.save()
                add_cat_form = CategoryForm()
                return HttpResponseRedirect(reverse("add_product"))
        elif 'add-subcategory-btn' in request.POST:
            add_subcat_form = SubCategoryForm(request.POST or None)
            if add_subcat_form.is_valid():
                obj = add_subcat_form.save(commit=False)
                obj.save()
                add_subcat_form = SubCategoryForm()
        else:
            pass

    context = {
        'add_category': add_cat_form,
        'add_subcategory': add_subcat_form,
    }

    return render(request, 'products/add_category.html', context)


# Add New Product view
@login_required
def add_product(request):
    """ A view to return the product detail page """

    def is_ajax(request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    all_categories = Category.objects.all()

    if is_ajax(request):
        category = request.GET.get('category')
        if category is not None:
            subcategories = SubCategory.objects.filter(
                category=category).order_by("display_name").values_list('display_name')
            subcategories_id = SubCategory.objects.filter(
                category=category).order_by("display_name").values_list('id')
            return JsonResponse({
                "subcategories_to_return": list(subcategories),
                "subcategories_id_to_return": list(subcategories_id),
                })

    add_cat_form = CategoryForm()
    add_subcat_form = SubCategoryForm()
    add_product_form = ProductForm()
    name_field = add_product_form.fields['name']
    name_field.widget = name_field.hidden_widget()
    code_field = add_product_form.fields['code']
    code_field.widget = code_field.hidden_widget()

    if request.method == "POST":
        if 'add-product-btn' in request.POST:
            add_product_form = ProductForm(request.POST or None, request.FILES)
            if add_product_form.is_valid():
                obj = add_product_form.save(commit=False)
                obj.save()
                add_product_form = ProductForm()
                name_field = add_product_form.fields['name']
                name_field.widget = name_field.hidden_widget()
                code_field = add_product_form.fields['code']
                code_field.widget = code_field.hidden_widget()

    context = {
        'all_categories': all_categories,
        'add_product': add_product_form,
    }

    return render(request, 'products/add_product.html', context)


@login_required
def all_handling_units(request):
    """ A view to show all hu's, including sorting and search queries """

    handling_units_with_units = HandlingUnit.objects.filter(qty_units="0", active=True).order_by("location")
    handling_units_with_packages = HandlingUnit.objects.filter(qty_units="1", active=True).order_by("location")
    products = Product.objects.all().order_by("display_name")
    companies = Company.objects.all().order_by("display_name")

    def is_ajax(request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    if request.GET:
        if 'company' and 'product' in request.GET:
            query_filter_company = request.GET['company']
            query_filter_product = request.GET['product']
            if query_filter_company != "" and query_filter_product != "":
                queries = Q(
                    company_id=query_filter_company) & Q(
                    product_id=query_filter_product)
                handling_units_with_units = handling_units_with_units.filter(queries)
                handling_units_with_packages = handling_units_with_packages.filter(queries)
            elif query_filter_company != "":
                queries = Q(
                    company_id=query_filter_company)
                handling_units_with_units = handling_units_with_units.filter(queries)
                handling_units_with_packages = handling_units_with_packages.filter(queries)
            elif query_filter_product != "":
                queries = Q(
                    product_id=query_filter_product)
                handling_units_with_units = handling_units_with_units.filter(queries)
                handling_units_with_packages = handling_units_with_packages.filter(queries)
            else:
                handling_units_with_units = handling_units_with_units
                handling_units_with_packages = handling_units_with_packages

    context = {
        'handling_units_with_units': handling_units_with_units,
        'handling_units_with_packages': handling_units_with_packages,
        'products': products,
        'companies': companies,
    }

    return render(request, 'products/handling_units.html', context)
