$(document).ready(function(){
    $("#create-bulk-retail-sale").click(function(){
        console.log("Button click received")
        let retailer = $("#retailer-select").val();
        let product = $("#product-select").val();
        let qty = $("#qty-select").val();
        console.log(retailer)
        console.log(product)
        console.log(qty)
        $.ajax({
            url: '',
            type: 'get',
            data: {
                retailer: retailer,
                product: product,
                qty: qty,
            },
            success: function(response){
                let subcategories = response.subcategories_to_return
                let subcategories_id = response.subcategories_id_to_return
                $.each(subcategories,function(key, value){
                    $("#id_subcategory").append('<option class="subcategory-value">' + value + '</option>');
                });
                let count = 0
                $.each(subcategories_id,function(key, value){
                    $(".subcategory-value").eq(count).attr('value', value);
                    count +=1
                });
            }
        });
    });
});