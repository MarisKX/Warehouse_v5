$(document).ready(function(){
    let lineItemCount = 0;
    $(".number-of-item").each(function () {
        lineItemCount += 1;
        $(this).text(lineItemCount);
    });
})