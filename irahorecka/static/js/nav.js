window.headroom_prevent_pin = false;

window.document.addEventListener("DOMContentLoaded", function (event) {

  // initialize headroom for banner
  var header = $('header').get(0);
  var headerHeight = header.offsetHeight;
  var headroom = new Headroom(header, {
    tolerance: 5,
    onPin : function() {
      if (window.headroom_prevent_pin) {
        window.headroom_prevent_pin = false;
        headroom.unpin();
      }
    }
  });
  headroom.init();
  // adds header space right upon instantiation for clean non-jumpy load
  $(".header-space").show();
  if(window.location.hash)
    headroom.unpin();
  $(header).addClass('headroom--transition');

  // offset scroll location for banner on hash change
  // (see: https://github.com/WickyNilliams/headroom.js/issues/38)
  window.addEventListener("hashchange", function(event) {
    window.scrollTo(0, window.pageYOffset - (headerHeight + 25));
  });

  // responsive menu
  $('.site-header').each(function(i, val) {
    var topnav = $(this);
    var toggle = topnav.find('.nav-toggle');
    toggle.on('click', function() {
      topnav.toggleClass('responsive');
    });
  });

  // nav dropdowns
  $('.nav-dropbtn').click(function(e) {
    $(this).next('.nav-dropdown-content').toggleClass('nav-dropdown-active');
    $(this).parent().siblings('.nav-dropdown')
       .children('.nav-dropdown-content').removeClass('nav-dropdown-active');
  });
  $("body").click(function(e){
    $('.nav-dropdown-content').removeClass('nav-dropdown-active');
  });
  $(".nav-dropdown").click(function(e){
    e.stopPropagation();
  });
});
