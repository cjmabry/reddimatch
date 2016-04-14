function match(element, match, match_type) {
  $.post('/accept', {
    username: match,
    match_type: match_type
  }).success(function(matched) {
    $(element).parent().removeClass("rejected");
    $(element).parent().addClass("accepted");
    $('.prompt').fadeOut(2000, function() { $(this).remove(); });
  });
}

function no_match(element, match, match_type) {

  $.post('/reject', {
    username: match,
    match_type: match_type
  }).success(function(matched) {
    $(element).parent().removeClass("accepted");
    $(element).parent().addClass("rejected");
    $('.prompt').fadeOut(2000, function() { $(this).remove(); });
  });

}

var timeout;

$(document).on("click", 'span.yes-match', function() {
  var match_username = $(this).attr("data-username");
  var match_type = $(this).attr("data-match-type");
  var match_button = $(this).parent();

  clearTimeout(timeout);
  timeout = setTimeout(function() {
      $(match_button).children(".text")[0].innerHTML="Accepted";
  }, 250);
  match(this, match_username, match_type);
});

$(document).on("click", 'span.no-match', function() {
  var match_username = $(this).attr("data-username");
  var match_type = $(this).attr("data-match-type");
  var match_button = $(this).parent();
  clearTimeout(timeout);
  timeout = setTimeout(function() {
      $(match_button).children(".text")[0].innerHTML="Rejected";
  }, 250);
  no_match(this, match_username, match_type);
});

var load_more = $('#load_more');
var offset = 1;
var custom_subs = null;
var user;

function display_more_results(response) {
  if (response != 'none') {
    data = response.data;

    for (var i in data) {
      user = data[i];

      console.log(user);

      var matches_div = $('.matches');

      match_div = $("<div>", {class: "match"});
      $(match_div).html("<img src='" + user.profile_photo_url +"' class='profile_photo'><div class='match_info'><h4><span class='username'>" + user.username + "</span></h4><p class='secondary-info'></p><p class='bio'></p><strong>Favorite Subs</strong><p class='sub-badges'></p></div><div class='match_button'><span class='check glyphicon glyphicon-ok yes-match' role='button' data-username='" + user.username + "' data-match-type='" + user.type + "'></span><span class='text'></span><span class='cross glyphicon glyphicon-remove no-match' role='button' data-username='" + user.username + "' data-match-type='" + user.type + "'></span></div>");

      if (user.bio) {
        var bio_div = $("<span>" + user.bio + "</span>");
        bio_div.appendTo(match_div.find('.bio'));
      }

      if (user.age) {
        var age_div = $("<span class='badge'>" + user.age + "</span>");
        age_div.appendTo(match_div.find('.secondary-info'));
      }

      if (user.distance) {
        var distance_div = $("<span class='badge'>" + user.distance + " miles away</span>");
        distance_div.appendTo(match_div.find('.secondary-info'));
      }

      if (user.gender) {
        var gender_div = $("<span class='badge'>" + user.gender + "</span>");
        gender_div.appendTo(match_div.find('.secondary-info'));
      }

      for (var sub in user.favorite_subs) {
        console.log(user.favorite_subs[sub]);
        var sub_div = $("<a class='badge' href=http://reddit.com/r/" + user.favorite_subs[sub] + ">/r/" + user.favorite_subs[sub] + "</a>");
        sub_div.appendTo(match_div.find('.sub-badges'));
      }

      matches_div.append(match_div);
    }
  } else {
    load_more.html('No more matches');
    load_more.addClass('disabled');
  }
}

$(document).on('click touch', '#load_more', function() {

  var type = $(this).attr("data-type");
  var url;
  custom_subs = $(this).attr("data-custom-subs");

  if (type == 'date') {
    url = '/date';
  } else {
    url = '/quick_match';
  }


  $.ajax({
    url:url,
    data: {
      "offset" : offset,
      "subs": custom_subs
    },
  type: 'GET'
  }).done(function (response) {
    console.log(response);
    offset++;
    display_more_results(response)
  });

});
