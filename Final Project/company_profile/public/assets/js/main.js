/** 
 * ===================================================================
 * main js
 *
 * ------------------------------------------------------------------- 
 */

(function ($) {
    "use strict";

    /* local validation */
    $('#contact-form').validate({

        /* submit via ajax */
        submitHandler: function (form) {

            var sLoader = $('#submit-loader'); // Add this loader element in HTML if needed

            $('#message-success').hide();

            $.ajax({

                type: "POST",
                url: "inc/sendMessage.php", // Change this to your actual backend URL
                data: $(form).serialize(),
                beforeSend: function () {
                    sLoader.fadeIn();
                },
                success: function (msg) {

                    // Message was sent
                    if (msg == 'OK') {
                        sLoader.fadeOut();
                        $('#message-warning').hide();
                        $('#contact-form').fadeOut();
                        $('#message-success').fadeIn();
                    }
                    // There was an error
                    else {
                        sLoader.fadeOut();
                        $('#message-warning').html(msg);
                        $('#message-warning').fadeIn();
                    }

                },
                error: function () {
                    sLoader.fadeOut();
                    $('#message-warning').html("Something went wrong. Please try again.");
                    $('#message-warning').fadeIn();
                }

            });
        }

    });

})(jQuery);
