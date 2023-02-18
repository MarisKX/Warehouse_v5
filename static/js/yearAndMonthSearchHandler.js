$(document).ready(function(){
    $('.year-select').each(function (index) { 
        if (index > 0) { 
            $(this).remove(); 
        } 
    });
    $('.month-select').each(function (index) { 
        if (index > 0) { 
            $(this).remove(); 
        } 
    });
})