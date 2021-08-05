$(document).ready(function() {
    // Prepend blank '-' option in #area - allows site-wide search
    $('#area').prepend('<option>-</option>');
    // Show load icon during ajax call.
    $("#query-new, #query-score").click(function(e) {
        e.preventDefault();
        var data = $(this).serialize();
        var url = $(this).attr('hx-post');
        // Will not display if screen size is for mobile / small.
        if ($(window).width() >= 768) {
            $loading.fadeIn(150);
        };
        $.post(url, data, function(response){
            $loading.fadeOut(150);
            // Scroll to bottom of page.
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
