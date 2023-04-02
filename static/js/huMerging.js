$(document).ready(function(){
    $(document).keyup(function(event) {
        if (event.keyCode == 13) {
            $("#next").click();
        }
    });
    let count = 0
    $("#next").click(function(){
        if (count < 1) {
            console.log("Click 1 detected");
            if( $(".hu-input-field").val().trim() == '' ) {
                $("#error-message").html("No HU was selected")
            } else {
                var hu1 = $('.hu-input-field').val();
                $("#selected-hu").append('<p id="firstHU">' + hu1 + '</p>');
                count += 1
                $('.hu-input-field').val('');
                $("#error-message").html("")
            };
        } else if (count < 2) {
            console.log("Click 2 detected");
            if( $(".hu-input-field").val().trim() == '' ) {
                $("#error-message").html("No HU was selected")
            } else {
                var hu2 = $('.hu-input-field').val();
                $("#selected-hu").append('<p id="secondHU">' + hu2 + '</p>');
                count += 1
                $('.hu-input-field').val('');
                $('.hu-input-field').attr('disabled', 'disabled');
                $("#next").html('Merge');
                $("#error-message").html("")
            }
        } else {
            let hu1 = $("#firstHU").html()
            let hu2 = $("#secondHU").html()
            console.log(hu1, hu2)

            $.ajax({
                url: '',
                type: 'get',
                data: {
                    hu1: hu1,
                    hu2: hu2,
                },
                success: function(response){
                    let error_message = response.error_message
                    console.log(error_message)
                    $("#error-message").html(error_message)
                    let success_message = response.success_message
                    console.log(success_message)
                    $("#success-message").html(success_message)
                    $("#next").html('Next');
                    $('.hu-input-field').prop("disabled", false);
                    $("#selected-hu").empty();
                }
            });
        }
    });
});