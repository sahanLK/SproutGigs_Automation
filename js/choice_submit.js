/*
Will be executed when clicking the submit button on job update dialog
*/

(function(field_id, val) {
    // append to existing value
    var field = $('#'+field_id);
    var existing = $(field).val();
    existing = (existing != "") ? existing += "\n" : existing;
    $(field).val(existing + val);
})(arguments[0], arguments[1])