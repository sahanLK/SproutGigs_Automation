/*
When the keylogger request something and the requested proof is not available, the user will
be notified changing the color of the page.
*/
$(document).ready(function() {
    $('body').css({'background-color': 'red'});

    function setToWhite() {
        $('body').css({'background-color': 'rgb(230, 230, 230)'});
    }

    counterInterval = setInterval(setToWhite, 350)
});