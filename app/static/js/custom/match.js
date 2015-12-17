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

$("span.yes-match").on("click", function() {
  var match_username = $(this).attr("data-username");
  var match_type = $(this).attr("data-match-type");
  match(this, match_username, match_type);
});

$("span.no-match").on("click", function() {
  var match_username = $(this).attr("data-username");
  var match_type = $(this).attr("data-match-type");
  no_match(this, match_username, match_type);
});
