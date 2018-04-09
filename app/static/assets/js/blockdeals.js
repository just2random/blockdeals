const steem = new dsteem.Client('https://api.steemit.com');

$(document).ready(function() {
  $('.loginbtn').click(function() {
    window.location.replace(sc2.getLoginURL());
  });
  if (sc2.getLoginURL() != "") {
    $('#loginbtn').prop("disabled", false);
  }
  $('.sidenav').sidenav();
  $('.datepicker').datepicker();
  $('.tooltipped').tooltip();
  $('.collapsible').collapsible();
  $("#country").countrySelect({
    defaultCountry: "",
    preferredCountries: ['au', 'ca', 'gb', 'us']
  });
  $(".dropdown-trigger").dropdown();

  $.get("/countries", function(data) {
    $.each(data, function(index, country_code) {
      $('#country_dropdown').append('<li><a class="truncate" href="/country/' + country_code + '"><div class="country-select"><div class="flag ' + country_code + '"></div></div> ' + countries[country_code] + '</a></li>');
      $('#mobile_freebies').after('<li><a class="truncate" href="/country/' + country_code + '"><div class="country-select"><div class="flag ' + country_code + '"></div></div> ' + countries[country_code] + '</a></li>');
    });
  });

  $('.votes').each(function(i, e) {
    steem.database.getState("/blockdeals/@" + $(e).data("author") + "/" + $(e).data("permlink")).then(function(d) {
      try {
        post = d['content'][$(e).data("author") + "/" + $(e).data("permlink")];
        if (post.author == $(e).data("author") && post.permlink == $(e).data("permlink")) {
          var up = 0;
          var dn = 0;
          var len = post['active_votes'].length;
          for (var i = 0; i < len; i++) {
            if (post['active_votes'][i].percent > 0) {
              up++;
            }
            else if (post['active_votes'][i].percent < 0) {
              dn++
            }
          }
          $(e).html("<i class='fas fa-thumbs-up fa-fw'></i> " + up +
              " / " + dn + " <i class='fas fa-thumbs-down fa-fw'></i>");
        }
        else {
          console.log("failed to find post: ", $(e).data("author"), $(e).data("permlink"));
          $(e).html("<i class='fas fa-fw fa-exclamation-circle text-red'></i>");
        }
      }
      catch(err) {
        console.log(err);
        $(e).html("<i class='fas fa-fw fa-exclamation-circle text-red'></i>");
      }
    }).catch(function(err) {
      console.log("failed to find post: ", $(e).data("author"), $(e).data("permlink"));
      $(e).html("<i class='fas fa-fw fa-exclamation-circle text-red'></i>");
    });
  });
});
