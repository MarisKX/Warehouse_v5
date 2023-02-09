$(document).ready(function(){
    let initList = $("#id_subcategory")
        if (initList[0].hasChildNodes()) {
            initList.empty();
    };
    let envTaxField = $("#id_enviroment_tax_amount")
        envTaxField.addClass('hidden');
        envTaxField.prev('label').addClass('hidden');
    $(document.body).on('change',"#id_category",function(){ // Used for system generated code
        let value = $(this).val()
        let list = $("#id_subcategory")
        if (list[0].hasChildNodes()) {
            list.empty()
        };
        $.ajax({
            url: '',
            type: 'get',
            data: {
                category: value
            },
            success: function(response){
                console.log(response)
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
    $("#id_enviroment_tax").change(function(){
        if ($("#id_enviroment_tax").is(':checked')) {
            $('#id_enviroment_tax_amount').removeClass("hidden")
            $('#id_enviroment_tax_amount').prev('label').removeClass('hidden');
        } else {
            $('#id_enviroment_tax_amount').addClass("hidden")
            $('#id_enviroment_tax_amount').prev('label').addClass('hidden');
        }
    });
    $("#toggle_add_category_btn").click(function(){
        $("#category-form").removeAttr('hidden');
        $("#toggle_add_category_h").prop('hidden', true);
        $("#toggle_add_category_btn").prop('hidden', true);
        console.log("clicked")
    });
    $("#close-category-form").click(function(){
        $("#toggle_add_category_h").removeAttr('hidden');
        $("#toggle_add_category_btn").removeAttr('hidden');
        $("#category-form").prop('hidden', true);
        console.log("clicked")
    });
    $("#toggle_add_subcategory_btn").click(function(){
        $("#subcategory-form").removeAttr('hidden');
        $("#toggle_add_subcategory_h").prop('hidden', true);
        $("#toggle_add_subcategory_btn").prop('hidden', true);
        console.log("clicked")
    });
    $("#close-subcategory-form").click(function(){
        $("#toggle_add_subcategory_h").removeAttr('hidden');
        $("#toggle_add_subcategory_btn").removeAttr('hidden');
        $("#subcategory-form").prop('hidden', true);
        console.log("clicked")
    });
});