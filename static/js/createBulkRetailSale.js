$(document).ready(function(){
    $(document.body).on('change',"#retailer-select",function(){
        let retailerCheck = $(this).val()
        $.ajax({
            url: '',
            type: 'get',
            data: {
                retailerCheck: retailerCheck,
            },
            success: function(response){
                let retailer_warehouses = response.retailer_warehouses
                let retailer_warehouses_value = response.retailer_warehouses_value
                $.each(retailer_warehouses,function(key, value){
                    $("#retailer-warehouse-select").append(
                        '<option class="warehouse-select" value=' + value + '>' + value + '</option>');
                });
                let count = 0
                $.each(retailer_warehouses_value,function(key, value){
                    $(".warehouse-select").eq(count).attr('value', value);
                    count +=1
                });
            }
        });
    });
    $("#create-bulk-retail-sale").click(function(){
        let retailer = $("#retailer-select").val();
        let retailerWarehouse = $("#retailer-warehouse-select").val();
        let product = $("#product-select").val();
        let qty = $("#qty-select").val();
        let price = +$("input[name='price']").val();
        $.ajax({
            url: '',
            type: 'get',
            data: {
                retailer: retailer,
                retailerWarehouse: retailerWarehouse,
                product: product,
                qty: qty,
                price: price,
            },
            success: function(response){
                console.log("Success")
                let retailInvoice = response.retailInvoice
                $.each(retailInvoice,function(key, value){
                    $(".response").append(
                        '<div>' + value + '</div>');
                });
            }
        });
    });
});