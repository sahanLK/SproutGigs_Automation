/*
The function that returns only the suitable textareas for proofs submission.
*/
function get_valid_textareas() {
    var formGroups = $('.form-group').toArray();    // All the form-groups
    var noLastGroup = formGroups.slice(0, formGroups.length - 1);   // Remove last form-group, which are buttons

    /*
    Removing file submission form-groups and storing only valid textareas.
    */
    const validTextareas = [];
    $.each( noLastGroup, function( index, val ) {
        if ( $(val).find('input[type="file"]').length == 0 ) {
            /*
            Find and store the textarea
            */
            var textarea = $( val ).find( 'textarea' );
            if ( textarea.length > 0 ) {
                validTextareas.push( textarea );
            } else {
                alert("CAUTION : Could not find a textarea inside a valid form-group.");
            }
        } else {
            console.log("Found a file submission");
        }
    } );
    return validTextareas;
}


$( document ).ready( function() {
    var validTextareas = get_valid_textareas();
    var minFieldNo = validTextareas.length > 0 ? minFieldNo = 1 : minFieldNo = 0;
    var maxFieldNo = validTextareas.length
    var currentFieldNo = parseInt( $( '#selected-field' ).text() );


    console.log("Min No: " + minFieldNo );

    var newVal;
    if ( currentFieldNo == maxFieldNo ) {
        newVal = minFieldNo;
    }
    if ( currentFieldNo < maxFieldNo ) {
        newVal = currentFieldNo + 1;
    }
    $( '#selected-field' ).text(newVal); //Update

    /*
    Add a nice border to the selected field and add a class.
    The added class will be used to clear the selected field text.
    */
    $( '.current-field' ).css({"border": "none"})   // Remove currently selected field border

    if ( validTextareas.length > 0 ) {
        var newField = $( validTextareas[newVal - 1] );  // Newly selected field
        $('html, body').animate({scrollTop: $( newField ).offset().top}, 1);    // Move to the newly selected field

        newField.css({"border": "5px solid #22ab59"});    // Add border to newly selected field
        $( '.current-field' ).removeClass('current-field');   // Remove currently selected field class
        newField.addClass('current-field');   // Add Class to the newly selected field
    }

} );
