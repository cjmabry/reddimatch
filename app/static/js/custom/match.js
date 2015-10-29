function match(element, match) {
  $.post('/accept', {
    match: match
  }).done(function(matched) {
    console.log('success');
    $(element).parent().parent().parent().css("background-color","#AFEAAF")
    $(element).parent().parent().parent().after("<div class='text-center'><small>" + match + " has been added to your matches!</br> <a href='/matches'>Go ahead and introuce yourself.</a></small></div>")
  }).fail(function(){
    console.log('fail');
  });
}

function no_match(element, match) {
  $(element).parent().parent().parent().css("background-color","#FF6D6D")
  $(element).parent().parent().parent().after("<div class='text-center'><small>You won't be matched with this person again.</small></div>")
}

$("a.yes-match").on("click", function() {
  var match_username = $(this).attr("data-username")
  match(this, match_username)
});

$("a.no-match").on("click", function() {
  var match_username = $(this).attr("data-username")
  no_match(this, match_username)
});
