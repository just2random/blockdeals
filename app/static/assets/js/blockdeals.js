const steem = new dsteem.Client('https://api.steemit.com');
username = "";

function voteup(e) {
  var parent_el = e.parentNode; // for closure
  var a = $(e.parentNode).data("author");
  var p = $(e.parentNode).data("permlink");
  $(e).addClass("fa-spin");
  $.get("/vote/" + a + "/" + p + "/up", function(data) {
    if (data['status']) { M.toast({html: 'Vote accepted'}) }
    else { M.toast({html: 'Vote failed: ' + data['msg']}) }
    update_votes(parent_el);
  }).fail(function() {
    M.toast({html: 'Vote failed'});
    update_votes(parent_el);
  });
}

function flag(e) {
  var parent_el = e.parentNode; // for closure
  var a = $(e.parentNode).data("author");
  var p = $(e.parentNode).data("permlink");
  $(e).addClass("fa-spin");
  $.get("/vote/" + a + "/" + p + "/flag", function(data) {
    if (data['status']) { M.toast({html: 'Flagged'}) }
    else { M.toast({html: 'Flag failed: ' + data['msg']}) }
    update_votes(parent_el);
  }).fail(function() {
    M.toast({html: 'Vote failed'});
    update_votes(parent_el);
  });
}

function update_votes(e) {
  steem.database.getState("/blockdeals/@" + $(e).data("author") + "/" + $(e).data("permlink")).then(function(d) {
    try {
      post = d['content'][$(e).data("author") + "/" + $(e).data("permlink")];
      if (post.author == $(e).data("author") && post.permlink == $(e).data("permlink")) {
        var up = 0;
        var dn = 0;
        var me = 0;
        var len = post['active_votes'].length;
        for (var i = 0; i < len; i++) {
          if (post['active_votes'][i].voter == username) {
            me = post['active_votes'][i].percent;
          }
          if (post['active_votes'][i].percent > 0) {
            up++;
          }
          else if (post['active_votes'][i].percent < 0) {
            dn++
          }
        }
        $(e).html("<i onclick='voteup(this)' class='vote fas fa-thumbs-up fa-fw " + ( me > 0 ? 'green-text' : '') + "'></i> " + up + " / " + dn + " <i onclick='flag(this)' class='vote fas fa-thumbs-down fa-fw " + ( me < 0 ? 'red-text' : '') + "'></i>");
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
}

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

  $.get("/whoami", function(data) {
    username = data['username'];
    $(".lazy").Lazy({
      votes: function(e) {
        update_votes(e);
      }
    });
  });

  $('#image_preview').on("error", function() {
    console.log('image_url appears invalid');
    $('#image_url').addClass("invalid");
  });

  $('#image_url').focusout(function() {
    console.log('image preview loading:', $(this).val());
    var img_url = $(this).val();
    $('#image_preview').attr('src', img_url);
  });
});
