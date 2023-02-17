$(document).ready(function(){
    let unitColumnTotal = 0;
    $(".amount_in_units").each(function () {
        unitColumnTotal += parseFloat($(this).text());
    });

    let calcOutputUnits = new Intl.NumberFormat("de-DE").format(unitColumnTotal);
    $("#total_amount_for_units").text(calcOutputUnits.replace(".", " ").replace(",", "."));

    let packageColumnTotal = 0;
    $(".amount_in_packages").each(function () {
        packageColumnTotal += parseFloat($(this).text());
    });

    let calcOutputPackages = new Intl.NumberFormat("de-DE").format(packageColumnTotal);
    $("#total_amount_for_packages").text(calcOutputPackages.replace(".", " ").replace(",", "."));
})