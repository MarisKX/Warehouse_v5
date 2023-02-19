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
    $('.month-select').each(function (index) { 
        let numbToMonth = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        };
        monthInNumber = $('.month-select').val()
        let month = numbToMonth[monthInNumber];
        $('.month-select').text(month)
    });
})