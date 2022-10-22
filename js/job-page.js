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
    /*
    Add Required page elements
    */
    // Time counter html element
    if ( $( '#time-counter' ).length == 0 ) {
        $( '.job-header__price' ).before( '<h4 id="time-counter"></h4>' );
    }
    $( 'a.navbar__post-job' ).css({"font-size": "25px", "padding": "3px 15px"});
    // Textarea Number html element
    if ( $( '#selected-field' ).length == 0 ) {
        $( '#time-counter' ).before( '<span id="selected-field"></span>' );
    }
    $( '#selected-field' ).css({"background-color": "#0077b3", "padding": "5px 10px", "margin": "0px 35px 0px 35px", "color": "white", "border-radius": "50%", "font-size": "20px", "font-weight": "700"});
    // Submission Field html element
    if ( $( '#submission-data' ).length == 0 ) {
        $( 'body' ).after( '<input type="textarea" id="submission-data" value="">' );
    }
    $( '#submission-data' ).css({"padding": "4px", "width": "100%", "position": "fixed", "bottom": "0px"});

    /*
    Setup the first default selected field, if available.
    and style the textarea for the first time.
    */
    var textareas = get_valid_textareas();
    if ( textareas.length > 0 ) {
        $( '#selected-field' ).text('1');   // Update selected field number
        $(textareas[0]).css({"border": "5px solid #22ab59"});   // Add a nice border
        $(textareas[0]).addClass('current-field');   // Add a Class
    } else {
        $( '#selected-field' ).text('0');   // Update selected field number
    }

    /*
    Events
    */
    // Submit the proof into the correct input field whenever the hidden input field value changes.
    $( '#submission-data' ).on( 'change', function() {
        var selectedFieldNo = $( '#selected-field' ).text();  // Get the field No.

        // Go ahead, only if field value change is not empty.
        if ( $( this ).val() !== "" ) {
            if ( textareas.length == 0 ) {
                alert( "WARNING: No textareas found !" );
            } else {
                console.log( 'Found ' + textareas.length + ' textareas.' );
                var submitField = $( textareas[ selectedFieldNo - 1 ] );
                newVal = submitField.val() + $( this ).val() + '\n';
                submitField.val( newVal ); // Update
            }
        }
    } );

    // Update Time Counter
    var mins = 0;
    var secs = 0;
    var displayMins = mins;
    var displaySecs = secs;

    function updateTimeCounter() {
        secs += 1;
        if (secs == 60) {
            secs = 0;
            mins += 1;
        }
        displaySecs = secs < 10 ? displaySecs = '0' + secs : displaySecs = secs;
        displayMins = mins < 10 ? displayMins = '0' + mins : displayMins = mins;
        $( '#time-counter' ).text( displayMins + ':' + displaySecs );
    }
    counterInterval = setInterval( updateTimeCounter, 1000 );

    /*
    Page Styling
    */
    // Hide Useless page content
    var uselessElems = {
        'nav_brand': '.navbar-brand',
        'nav_ul': '.d-none ul',
        'nav_switch_profile': '.switch-profile-text--desktop',
        'notice': '.site-notice',
        'sub_header': '.sub-header__back',
        'job_info': '.job-info',
        'row': '.row.mb-8.mt-8',
        'line': '.side-popup__line',
        'job_info_rest': '.mt-4.pl-5',
        'navbar': '.navbar-wrapper',
        'job_header': '.job-header__price',
    };
    $.each( uselessElems, function( key, selector ) {
        $(selector).hide();
    });

    // Style the page
    $('.content-area').css({"padding": "0px"});
    $('.job-header__price small').css({"display": "none"});
    $('.job-header__rate.text-right').css({"display": "flex"});
    $('#time-counter').css({"padding": "7px 20px", "background-color": "#22ab59", "color": "#fff", "font-size": "22px", "margin-bottom": "0px", "font-weight": "400", "font-family": "monospace"});
    $('.job-header').css({"position": "fixed", "top": "0px", "width": "100%", "z-index": "200", "background-color": "#f2f2f2", "padding": "10px 15px", "box-shadow": "0 2px 5px 0 rgb(0 0 0 / 16%), 0 2px 10px 0 rgb(0 0 0 / 12%)"});
    $('.job-header p.mb-0').css({"display": "none"});
    $('.row:nth-child(1)').css({"margin-top": "70px"});
    $('h1.headline').css({"font-size": "22px", "padding-top": "6px"});
    $('body').css({"background-color": "#e6e6e6", "padding-bottom": "15px"});
    $('footer').css({"display": "none"});
    $('li.py-1').css({"font-size": "16px", "font-weight": "500", "color": "#6b6b47"});
    $('label').css({"font-size": "18px", "font-weight": "500", "color": "#6b6b47"});
    $('.form-group').css({"margin-bottom": "5px"});
    $('.form-group label').css({"margin-bottom": "0px"});
    $('.smooth-scroll').parent().parent().hide();   // Hide submit proofs button
    $('.hide-job').parent().parent().parent().parent().parent().addClass('col-md-12');

    var jobInfoSections = $('div.job-info-list');
    var rows = $('.row');

    $( jobInfoSections[0] ).hide();   // Hide hold this job section
    $( jobInfoSections[2] ).hide();   // Remove required proofs section.
    $( jobInfoSections[3] ).hide();   // Remove "Submit your proofs below" title

    var jobInfoListHeadings = $('.job-info-list__heading');
    $(jobInfoListHeadings[1]).hide(); // Remove "What is expected from workers?" title

} );
