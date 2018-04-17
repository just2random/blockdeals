const steem = new dsteem.Client('https://api.steemit.com');
username = "";

function voteup(e) {
  var parent_el = e.parentNode.parentNode; // for closure
  var a = $(parent_el).data("author");
  var p = $(parent_el).data("permlink");
  $(parent_el).find(".upVoteThumb").addClass("fa-spin");
  $.get("/vote/" + a + "/" + p + "/up", function(data) {
    if (data['status']) { M.toast({html: 'Vote accepted'}) }
    else { M.toast({html: 'Vote failed: ' + data['msg']}) }
    update_votes(parent_el);
    $(parent_el).find(".upVoteThumb").removeClass("fa-spin");
  }).fail(function() {
    M.toast({html: 'Vote failed'});
    update_votes(parent_el);
    $(parent_el).find(".upVoteThumb").removeClass("fa-spin");
  });
}

function flag(e) {
  var parent_el = e.parentNode.parentNode; // for closure
  var a = $(parent_el).data("author");
  var p = $(parent_el).data("permlink");
  $(parent_el).find(".dnVoteThumb").addClass("fa-spin");
  $.get("/vote/" + a + "/" + p + "/flag", function(data) {
    if (data['status']) { M.toast({html: 'Flagged'}) }
    else { M.toast({html: 'Flag failed: ' + data['msg']}) }
    update_votes(parent_el);
    $(parent_el).find(".dnVoteThumb").removeClass("fa-spin");
  }).fail(function() {
    M.toast({html: 'Vote failed'});
    update_votes(parent_el);
    $(parent_el).find(".dnVoteThumb").removeClass("fa-spin");
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
        $(e).find(".upVote").text(up);
        $(e).find(".dnVote").text(dn);
        if (me > 0) {
          $(e).find(".upVoteThumb").addClass('green-text');
          $(e).find('.supporter').fadeIn();
        } else if (me < 0) {
          $(e).find(".dnVoteThumb").addClass('red-text');
        }
      }
      else {
        console.log("failed to find post: ", $(e).data("author"), $(e).data("permlink"));
        $(e).html("<div class='col s12 center-align'><i class='fas fa-fw fa-exclamation-circle red-text' title='Error reading votes'></i></div>");
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

  $('.fixed-action-btn').floatingActionButton();
});
