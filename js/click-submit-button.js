$( document ).ready( function() {
    var submitButton = $( '#submit-proof-btn' );

    if ( submitButton.length > 0 ) {
        try {
            $('html, body').animate({
                scrollTop: $( submitButton ).offset().top
            }, 1);
            $( submitButton ).click();
            console.log("Click Success: Submit Button");
        } catch {
            console.log("Click failed: Submit Button");
        }
    }
} );