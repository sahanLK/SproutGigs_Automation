/*
This Js code check if the configured values are correctly set or not,
by comparing configured values with actual values.
Always run this code before opening sproutGigs site url.
*/

/* Changing the colors if the configured to and actual values don't match */
return( function() {
    var tBodies = $('tbody');   // all table bodies
    $.each(tBodies, function(index, tBody) {
        var tRows = $(tBody).find('tr');    // all table roes
        $.each(tRows, function( index, tRow ) {
            var tDatas = $(tRow).find('td');    // all tds in current tr
            var configuredTo = $(tDatas[1]).text();
            var actual = $(tDatas[2]).text();

            /* Change python bools into Js bools */
            configuredTo = ( configuredTo == 'True' ) ? 'true': configuredTo;
            configuredTo = ( configuredTo == 'False' ) ? 'false': configuredTo;
            actual = ( actual == 'True' ) ? 'true': actual;
            actual = ( actual == 'False' ) ? 'false': actual;
            if( configuredTo != actual) {
                $(tRow).css({"background-color": "red", "color": "white"});
                return false;
            }
        });
    });
    return true;
})()
