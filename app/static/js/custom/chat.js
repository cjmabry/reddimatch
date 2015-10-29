$(document).ready(function(){
  var socket = io.connect('http://' + document.domain + ':' + location.port);
  socket.on('connect', function() {
      socket.emit('my event', {data: 'I\'m connected!'});
      console.log('connected');
  });

  var current_user;

  $("ul#user_list li").on("touchstart click", function() {
    current_user = $(this).attr("data-username");
    $('.selected').removeClass('selected');
    $(this).addClass("selected");
    $("#conversation_heading").html(current_user);
  });

  var textarea = ("#enter_message");

  $(textarea).on('keyup', function() {

    var content = $(this).val();

    if(content.replace(/\s/g, "").length > 0) {
      $(submit_message).addClass("has_content");
      console.log(content);
    } else {
      $(submit_message).removeClass("has_content");
    }

  });

  $("#submit_message").on('click', function() {

    if($(this).hasClass("has_content")) {
      var message = $("#enter_message").val();
      console.log(message)

      socket.emit('message', {data: message});
    }
  });

  socket.on('message response', function(msg) {
    $("#current_conversation #messages").append(msg.data);
  });

});
