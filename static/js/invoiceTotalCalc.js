$(document).ready(function(){
    let amountColumnTotal = 0;
    let docCount = 0;
    $(".invoice-amount-total").each(function () {
        amountColumnTotal += parseFloat($(this).text());
        docCount += 1;
    });

    let calcOutputAmount = amountColumnTotal.toFixed(2);
    $("#invoice-amount-total").text(calcOutputAmount);

    let btwColumnTotal = 0;
    $(".invoice-btw-total").each(function () {
        btwColumnTotal += parseFloat($(this).text());
    });

    let calcOutputBTW = btwColumnTotal.toFixed(2);
    $("#invoice-btw_total").text(calcOutputBTW);

    let amountAndBtwColumnTotal = 0;
    $(".invoice-amount-total_with_btw").each(function () {
        amountAndBtwColumnTotal += parseFloat($(this).text());
    });

    let calcOutputAmountwBTW = amountAndBtwColumnTotal.toFixed(2);
    $("#invoice-amount_total_with_btw").text(calcOutputAmountwBTW);

    $("#invoice-count").text(docCount);
})