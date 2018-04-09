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
    steem.database.getDiscussions('active', {select_authors: [$(e).data("author")], start_author: $(e).data("author"), start_permlink: $(e).data("permlink"), limit: 1}).then(function(d) {
      if (d[0].author == $(e).data("author") && d[0].permlink == $(e).data("permlink")) {
        $(e).html("<i class='fas fa-thumbs-up fa-fw'></i> " + d[0]['active_votes'].length);
      }
      else {
        console.log("failed to find post: ", $(e).data("author"), $(e).data("permlink"));
        $(e).html("");
      }
    }).catch(function(err) {
      console.log("failed to find post: ", $(e).data("author"), $(e).data("permlink"));
      $(e).html("");
    });
  });
});
