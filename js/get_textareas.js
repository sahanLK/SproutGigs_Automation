/*
This file does not use by any python file, instead will be used in other js files.
This function is used to get all the suitable proofs submissions textareas after necessary filtering.
File was created for modular programming but cannot be implemented yet.
*/


function get_valid_textareas() {
    var formGroups = $('.form-group').toArray();    // All the form-groups
    var noLastGroup = formGroups.slice(0, formGroups.length - 1);   // Remove last form-group, which are buttons

    /*
    Removing file submission form-groups and storing only valid textareas.
    */
    const validTextareas = [];
    $.each( noLastGroup, function( index, val ) {
        if ( $( val ).find('input[type="file"]').length == 0 ) {
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
