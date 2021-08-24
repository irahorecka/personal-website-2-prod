$(document).ready(function() {
    // Prepend blank '-' option in #area - allows site-wide search
    $('#area').prepend('<option>-</option>');
    // NOTE: you'll see two equivalent POST requests being made to Flask routes that are
    // triggered by #query-new and #query-score. The first is from `hx-post` and the second
    // is from the AJAX event handler below.
    $("#query-new, #query-score").click(function(e) {
        e.preventDefault();
        var url = $(this).attr('hx-post');
        var data = $('form').serialize();
        // Show load icon during AJAX call.
        // Will not display if screen size is for mobile / small.
        if ($(window).width() >= 768) {
            $loading.fadeIn(150);
        };
        $.post(url, data, function(response){
            $loading.fadeOut(150);
            // Diminish load icon during AJAX call. Scroll to bottom of page.
            $("html, body").animate({ scrollTop: document.body.scrollHeight }, "slow");
        });
    });
});

function swapRandom(parentID, childTag) {
    // Get id of parent element and randomly sample its child tag.
    var select = document.getElementById(parentID);
    var items = select.getElementsByTagName(childTag);
    var index = Math.floor(Math.random() * items.length);
    select.selectedIndex = index;
}
