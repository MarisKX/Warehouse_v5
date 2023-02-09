$(document).ready(function(){
    let initList = $(".subcategory-search-list")
        if (initList[0].hasChildNodes()) {
            initList.empty();
            initList.attr('disabled', true)
            $(".subcategory-search-list").append('<option value="">Select All</option>');
    };
    $(document.body).on('change',".category-search-list",function(){
        let value = $(this).val()
        let list = $(".subcategory-search-list")
        if (list[0].hasChildNodes()) {
            list.empty()
        };
        $(".subcategory-search-list").append('<option value="">Select All</option>');

        $.ajax({
            url: '',
            type: 'get',
            data: {
                category: value
            },
            success: function(response){
                let subcategories = response.subcategories_to_return
                let subcategories_id = response.subcategories_id_to_return
                $.each(subcategories,function(key, value){
                    $(".subcategory-search-list").append('<option class="subcategory-value">' + value + '</option>');
                    $(".subcategory-search-list").attr('disabled', false)
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
