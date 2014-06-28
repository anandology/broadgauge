
function setup_browserid(options) {
  var defaultOptions = {
    currentUser: null,
    siteName: 'Broad Guage'
  };

  options = $.extend({}, defaultOptions, options);   

  $(function() {
      $(".browserid-login").click(function() {
          var next = $(this).attr("href");
          if (!next || next[0] != "/")
            next = document.location.pathname + document.location.search;
          navigator.id.request({'siteName': options.siteName, 'returnTo': next});
      });
      $(".browserid-logout").click(function() {
          navigator.id.logout(); 
      });
  });

  navigator.id.watch({
    loggedInUser: options.currentUser,
    onlogin: function(assertion) {
      // A user has logged in! Here you need to:
      // 1. Send the assertion to your backend for verification and to create a session.
      // 2. Update your UI.
      $.ajax({ /* <-- This example uses jQuery, but you can use whatever you'd like */
        type: 'POST',
        url: '/auth/login', // This is a URL on your website.
        data: {assertion: assertion},
        success: function(res, status, xhr) { window.location.reload(); },
        error: function(xhr, status, err) {
          //navigator.id.logout();
          alert("Login failure: " + err);
        }
      });
    },
    onlogout: function() {
      // A user has logged out! Here you need to:
      // Tear down the user's session by redirecting the user or making a call to your backend.
      // Also, make sure loggedInUser will get set to null on the next page load.
      // (That's a literal JavaScript null. Not false, 0, or undefined. null.)
      $.ajax({
        type: 'POST',
        url: '/auth/logout', // This is a URL on your website.
        success: function(res, status, xhr) { window.location.reload(); },
        error: function(xhr, status, err) { alert("Logout failure: " + err); }
      });
    }
  });
}
