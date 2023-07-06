$(document).ready(function(){
    ///let firstItemRow = $(".product-table").find(".formset-row").first().removeAttr('hidden');
    let todayTop = $("#todayTop").text();
    let dateObj = moment(todayTop, "MMM. DD, YYYY");
    let todayTopFormatted = dateObj.format("YYYY-MM-DD");
    let invoiceNumberP = $("form").find("div").first();
    invoiceNumberP.addClass("col-3 offset-4 form-row mb-5");

    let supplier = $("form").find("div").eq(1).addClass("col-4 offset-2");
    let customer = $("form").find("div").eq(2).addClass("col-4");
    let wrapper = $('<div class="row form-row"></div>');
    supplier.add(customer).wrapAll(wrapper.clone());

    let supplier_warehouse = $("form").find("div").eq(4).addClass("col-4 offset-2");
    let customer_warehouse = $("form").find("div").eq(5).addClass("col-4");
    let warehouse_wrapper = $('<div class="row form-row mb-5"></div>');
    supplier_warehouse.add(customer_warehouse).wrapAll(warehouse_wrapper.clone());
    
    let date = $("form").find("div").eq(7).addClass("col-4 offset-2")
    $("#id_date").val(todayTopFormatted).attr('readonly', true).addClass("not-allowed");
    let payment_term = $("form").find("div").eq(8).addClass("col-4 offset-2");

    let elements = $('.formset-row:not([hidden])');

    let initSuplierWarehouseList = $("#id_suplier_warehouse");
    if (initSuplierWarehouseList[0].hasChildNodes()) {
        initSuplierWarehouseList.children().filter(function() {
            return $(this).val() !== "NotSelected";
        }).remove();
    }

    $(document.body).on('change',"#id_suplier",function(){ // Used for system generated code
        let value = $(this).val()
        let initSuplierWarehouseList = $("#id_suplier_warehouse");
        if (initSuplierWarehouseList[0].hasChildNodes()) {
            initSuplierWarehouseList.children().filter(function() {
                return $(this).val() !== "NotSelected";
            }).remove();
        }
        $.ajax({
            url: '',
            type: 'get',
            data: {
                id_suplier: value
            },
            success: function(response){
                let suplierWarehouseList = response.suplier_warehouse
                let suplierWarehouseListId = response.id_suplier_warehouse
                $.each(suplierWarehouseList,function(key, value){
                    $("#id_suplier_warehouse").append('<option class="suplier-warehouse-value">' + value + '</option>');
                });
                let count = 0
                $.each(suplierWarehouseListId,function(key, value){
                    $(".suplier-warehouse-value").eq(count).attr('value', value);
                    count +=1
                });
            }
        });   
    });

    let initCustomerWarehouseList = $("#id_customer_warehouse");
    if (initCustomerWarehouseList[0].hasChildNodes()) {
        initCustomerWarehouseList.children().filter(function() {
            return $(this).val() !== "NotSelected";
        }).remove();
    }

    $(document.body).on('change',"#id_customer",function(){ // Used for system generated code
        let value = $(this).val()
        let initCustomerWarehouseList = $("#id_customer_warehouse");
        if (initCustomerWarehouseList[0].hasChildNodes()) {
            initCustomerWarehouseList.children().filter(function() {
                return $(this).val() !== "NotSelected";
            }).remove();
        }
        $.ajax({
            url: '',
            type: 'get',
            data: {
                id_customer: value
            },
            success: function(response){
                let customerWarehouseList = response.customer_warehouse
                let customerWarehouseListId = response.id_customer_warehouse
                $.each(customerWarehouseList,function(key, value){
                    $("#id_customer_warehouse").append('<option class="customer-warehouse-value">' + value + '</option>');
                });
                let count = 0
                $.each(customerWarehouseListId,function(key, value){
                    $(".customer-warehouse-value").eq(count).attr('value', value);
                    count +=1
                });
            }
        });   
    });

    $(document.body).on('change',"#id_suplier_warehouse",function(){ // Used for system generated code
        let value = $(this).val()
        console.log(value)
        let initProductList = $("#id_lineitems-0-product");
        if (initProductList[0].hasChildNodes()) {
            initProductList.children().filter(function() {
                return $(this).val() !== "NotSelected";
            }).remove();
        }
        $.ajax({
            url: '',
            type: 'get',
            data: {
                id_warehouse: value
            },
            success: function(response){
                console.log(response)
                let product_ids = response.product_ids
                let products_display_names_in_stock = response.products_display_names_in_stock
                $.each(products_display_names_in_stock,function(key, value){
                    $("#id_lineitems-0-product").append('<option class="product-in-stock-list">' + value + '</option>');
                });
                let count = 0
                $.each(product_ids,function(key, value){
                    $(".product-in-stock-list").eq(count).attr('value', value);
                    count +=1
                });
            }
        });   
    });

    elements.each(function() {
        $(this).change(function() {
        console.log("Change detected");
        let amount = $(this).find("input").first().val();
        console.log(amount);
        let price = $(this).closest('.formset-row').find("input").eq(1).val();
        console.log(price);
        let total = amount * price;
        console.log(parseFloat(total.toFixed(2)));
        $(this).find("td").eq(4).text(total.toFixed(2));
        let btw = (total / 100) * 21;
        console.log(parseFloat(btw.toFixed(2)));
        $(this).find("td").eq(5).text(btw.toFixed(2));
        let totalWithBTW = total + btw
        console.log(parseFloat(totalWithBTW.toFixed(2)));
        $(this).find("td").eq(6).text(totalWithBTW.toFixed(2));
        let itemCount = 0;
        let totalCount = 0;
        let btwCount = 0;
        let totalWithBtw = 0;
        $('.formset-row:not([hidden])').find(".total").each(function () {
            itemCount += 1;
            totalCount += parseFloat($(this).text());
        });
        $('.formset-row:not([hidden])').find(".btw").each(function () {
            btwCount += parseFloat($(this).text());
        });
        $('.formset-row:not([hidden])').find(".total-with-btw").each(function () {
            totalWithBtw += parseFloat($(this).text());
        });
        console.log(itemCount)
        console.log(totalCount)
        $(".itemCount").text(itemCount);
        $(".calculatedTotal").text(totalCount.toFixed(2));
        $(".calculatedBTW").text(btwCount.toFixed(2));
        $(".calculatedTotalWithBTW").text(totalWithBtw.toFixed(2));
        });
    });


    let formCount = $('#id_lineitems-TOTAL_FORMS').val();
    console.log(formCount)

    // Event listener for the "Add Item" button
    $('#add-row').click(function() {
        // Clone the first form in the formset
        var newForm = $('table tr:last').clone();

        // Update form IDs, names, and indices
        let firstSelectField = newForm.find('td').find('select').first()
        firstSelectField.removeAttr('name');
        firstSelectField.removeAttr('id');
        let newNameProduct = 'lineitems-' + formCount + '-product';
        let newIDProduct = 'id_lineitems-' + formCount + '-product';
        console.log(newNameProduct)
        console.log(newIDProduct)
        firstSelectField.attr('name', newNameProduct);
        firstSelectField.attr('id', newIDProduct);

        let secondField = newForm.find('td').find('input').eq(0)
        secondField.removeAttr('name');
        secondField.removeAttr('id');
        let newNameQty = 'lineitems-' + formCount + '-qty';
        let newIDQty = 'id_lineitems-' + formCount + '-qty';
        console.log(newNameQty)
        console.log(newIDQty)
        secondField.attr('name', newNameQty);
        secondField.attr('id', newIDQty);

        let thirdField = newForm.find('td').find('select').eq(1)
        thirdField.removeAttr('name');
        thirdField.removeAttr('id');
        let newNameUnitsIn = 'lineitems-' + formCount + '-qty_in';
        let newIDUnitsIn = 'id_lineitems-' + formCount + '-qty_in';
        console.log(newNameUnitsIn)
        console.log(newIDUnitsIn)
        thirdField.attr('name', newNameUnitsIn);
        thirdField.attr('id', newIDUnitsIn);

        let fourthField = newForm.find('td').find('input').eq(1)
        fourthField.removeAttr('name');
        fourthField.removeAttr('id');
        let newNamePrice = 'lineitems-' + formCount + '-price';
        let newIDPrice = 'id_lineitems-' + formCount + '-price';
        fourthField.attr('name', newNamePrice);
        fourthField.attr('id', newIDPrice);

        // Append the new form to the formset table
        $('table').append(newForm);

        // Increment the form count
        formCount++;

        // Pre-defined variable
        let newId = formCount;
        console.log(newId)

        // Find the element using its name attribute
        let hiddenElement = $('#id_lineitems-TOTAL_FORMS');

        // Change the id attribute to the new value
        hiddenElement.val(newId);

        let elements = $('.formset-row:not([hidden])');

        elements.each(function() {
            $(this).change(function() {
            console.log("Change detected");
            let amount = $(this).find("input").first().val();
            console.log(amount);
            let price = $(this).closest('.formset-row').find("input").eq(1).val();
            console.log(price);
            let total = amount * price;
            console.log(parseFloat(total.toFixed(2)));
            $(this).find("td").eq(4).text(total.toFixed(2));
            let btw = (total / 100) * 21;
            console.log(parseFloat(btw.toFixed(2)));
            $(this).find("td").eq(5).text(btw.toFixed(2));
            let totalWithBTW = total + btw
            console.log(parseFloat(totalWithBTW.toFixed(2)));
            $(this).find("td").eq(6).text(totalWithBTW.toFixed(2));
            let itemCount = 0;
            let totalCount = 0;
            let btwCount = 0;
            let totalWithBtw = 0;
            $('.formset-row:not([hidden])').find(".total").each(function () {
                itemCount += 1;
                totalCount += parseFloat($(this).text());
            });
            $('.formset-row:not([hidden])').find(".btw").each(function () {
                btwCount += parseFloat($(this).text());
            });
            $('.formset-row:not([hidden])').find(".total-with-btw").each(function () {
                totalWithBtw += parseFloat($(this).text());
            });
            console.log(itemCount)
            console.log(totalCount)
            $(".itemCount").text(itemCount);
            $(".calculatedTotal").text(totalCount.toFixed(2));
            $(".calculatedBTW").text(btwCount.toFixed(2));
            $(".calculatedTotalWithBTW").text(totalWithBtw.toFixed(2));
            });
        });
    });
})