// TO-DO: auto expand text box

$(document).ready(function(){
  var current_user, has_content = false;

  current_user = $('.selected').attr("data-username");

  console.log("Current user: " + current_user);

  var socket = io.connect('http://' + document.domain + ':' + location.port);
  socket.on('connect', function() {
      socket.emit('join', {username: current_user});
      console.log('connected');
  });

  $("ul#user_list li").on("touchstart click", function() {
    current_user = $(this).attr("data-username");
    $('.selected').removeClass('selected');
    $(this).addClass("selected");
    $("#conversation_heading").html(current_user);
    console.log("Current user: " + current_user);
    socket.emit('join', {username: current_user});
  });

  var textarea = ("#enter_message");

  $(textarea).on('keyup', function() {

    var content = $(this).val();

    if(content.replace(/\s/g, "").length > 0) {
      $(submit_message).addClass("has_content");
      has_content = true;
    } else {
      $(submit_message).removeClass("has_content");
      has_content = false;
      $(textarea).attr("placeholder", "Type a message...");
    }

  });

  $(textarea).keypress(function(event) {
    var keycode = (event.keyCode ? event.keyCode : even.which);

    if(keycode == '13' && !event.shiftKey && has_content) {
      submit($(this).val());
      $(this).val("");
      event.preventDefault();
    }

    if(keycode == '13' && !event.shiftKey && !has_content) {
      event.preventDefault();
    }

  });

  $("#submit_message").on('click', function() {
    var content = $("#enter_message").val();
    submit(content);
    $("#enter_message").val("");
  });

  submit = function(content) {
    socket.emit('message', {msg: content, to: current_user, from:'from'});
  }

  socket.on('message response', function(data) {

    var div;

    div = $("<div>", {class: "message"});
    $(div).text(data.msg);

    $("#current_conversation #current_messages").append(div);
  });

  // $(textarea).on("input", function() {
  //   $(this).height = "";
  //   $(this).height = Math.min(textarea.scrollHeight, 300) + "px";
  //
  // });

});
