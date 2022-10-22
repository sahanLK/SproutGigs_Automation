/*
If textarea id is given, find the field with the given id and clear it. Otherwise,
clear get the textarea number from the job page and clear it appropriately.
*/

// Self Invoking.
(function(fieldId) {
    try {
        if ( fieldId ) {
            console.log('field id is given', fieldId);
            $( '#'+fieldId ).val('');
        } else {
            console.log('no field id');
            $( '.current-field' ).val('');
        }
    } catch (err) {
            alert("Error from clear-textarea.js \n\n"+ err.name+ ': ' + err.message);
        }
}) (arguments[0]);
