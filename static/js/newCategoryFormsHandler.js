$(document).ready(function(){
    $("#toggle_add_category_btn").click(function(){
        $("#category-form").removeAttr('hidden');
        $("#toggle_add_category_h").prop('hidden', true);
        $("#toggle_add_category_btn").prop('hidden', true);
    });
    $("#close-category-form").click(function(){
        $("#toggle_add_category_h").removeAttr('hidden');
        $("#toggle_add_category_btn").removeAttr('hidden');
        $("#category-form").prop('hidden', true);
    });
    $("#toggle_add_subcategory_btn").click(function(){
        $("#subcategory-form").removeAttr('hidden');
        $("#toggle_add_subcategory_h").prop('hidden', true);
        $("#toggle_add_subcategory_btn").prop('hidden', true);
    });
    $("#close-subcategory-form").click(function(){
        $("#toggle_add_subcategory_h").removeAttr('hidden');
        $("#toggle_add_subcategory_btn").removeAttr('hidden');
        $("#subcategory-form").prop('hidden', true);
    });
});