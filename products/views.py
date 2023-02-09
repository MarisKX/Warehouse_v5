# General imports
from django.shortcuts import render, get_object_or_404, reverse
from django.http import JsonResponse, HttpResponseRedirect
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
from .models import Product, Category, SubCategory
# Form imports
from .forms import ProductForm, CategoryForm, SubCategoryForm


# All Products view
def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all().order_by("display_name")
    all_categories = Category.objects.all()

    context = {
        'products': products,
        'all_categories': all_categories,
    }

    return render(request, 'products/products.html', context)


# Product Details View
def product_details(request, code):
    """ A view to return the product detail page """

    product = get_object_or_404(Product, code=code)

    context = {
        'product': product,
    }

    return render(request, 'products/product_details.html', context)


# Product Details View in PDF
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
    textobj_reg = c.beginText()
    textobj_reg.setTextOrigin(45, 160)
    textobj_reg.setFont("Helvetica", 14)
    textobj_xl = c.beginText()
    textobj_xl.setTextOrigin(45, 100)
    textobj_xl.setFont("Helvetica", 30)
    textobj_sm = c.beginText()
    textobj_sm.setTextOrigin(310, 120)
    textobj_sm.setFont("Helvetica", 8)
    textobj_sm.setCharSpace(8)

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
        " ",
        "Enviroment Tax:",
        env_tax_amount + " Eur",
    ]

    lg_lines = [
        " ",
        "Name:",
        product.display_name,
    ]

    article = product.code
    barcode = product.code.lower()
    # barcode = "12341570"

    for line in lg_lines:
        textobj_reg.setFont("Helvetica", 18)
        textobj_reg.textLine(line)

    for line in reg_lines:
        textobj_reg.setFont("Helvetica", 14)
        textobj_reg.textLine(line)

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
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=f"" + product.display_name + "_" + product.code.lower() + ".pdf")


# Add New Product view
def add_product(request):
    """ A view to return the product detail page """

    def is_ajax(request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    all_categories = Category.objects.all()

    if is_ajax(request):
        category = request.GET.get('category')
        if category is not None:
            subcategories = SubCategory.objects.filter(
                category=category).values_list('display_name')
            subcategories_id = SubCategory.objects.filter(
                category=category).values_list('id')
            print(subcategories_id, subcategories)
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
        if 'add-category-btn' in request.POST:
            add_cat_form = CategoryForm(request.POST or None)
            if add_cat_form.is_valid():
                obj = add_cat_form.save(commit=False)
                print(obj)
                obj.save()
                add_cat_form = CategoryForm()
                return HttpResponseRedirect(reverse("add_product"))
        elif 'add-subcategory-btn' in request.POST:
            add_subcat_form = SubCategoryForm(request.POST or None)
            if add_subcat_form.is_valid():
                obj = add_subcat_form.save(commit=False)
                obj.save()
                add_subcat_form = SubCategoryForm()
        elif 'add-product-btn' in request.POST:
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
        'add_category': add_cat_form,
        'add_subcategory': add_subcat_form,
        'add_product': add_product_form,
    }

    return render(request, 'products/add_product.html', context)