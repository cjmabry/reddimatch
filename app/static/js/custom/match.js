function match(element, match) {
  $.post('/accept', {
    username: match
  }).success(function(matched) {
    $(element).parent().removeClass("rejected");
    $(element).parent().addClass("accepted");
    $('.prompt').fadeOut(2000, function() { $(this).remove(); });
  });
}

function no_match(element, match) {

  $.post('/reject', {
    username: match
  }).success(function(matched) {
    $(element).parent().removeClass("accepted");
    $(element).parent().addClass("rejected");
    $('.prompt').fadeOut(2000, function() { $(this).remove(); });
  });

}

$("span.yes-match").on("click", function() {
  var match_username = $(this).attr("data-username");
  match(this, match_username);
});

$("span.no-match").on("click", function() {
  var match_username = $(this).attr("data-username");
  no_match(this, match_username);
});
