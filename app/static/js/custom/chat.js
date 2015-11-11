// TODO: auto expand text box
// TODO: auto scroll text box/ show notification
// TODO: get user info

var properties, Chat = {

  properties : {
      url : 'http://' + document.domain + ':' + location.port,
      username: null,
      object: null,
      userList: $("ul#user_list"),
      currentUser : null,
      hasContent: false,
      messageBox: $("#enter_message"),
      currentMessages: $("#current_messages")
  },

  init: function() {
    p = this.properties;
    this.connect();
    this.ui_handlers();
    this.chat_handlers();
  },

  connect: function() {
    p.object = io.connect(p.url);
    this.set_username();
  },

  set_username: function() {
    $.get("/get_username", function(data) {
        p.username = data.username;
    });
  },

  get_current_username: function() {
    p.currentUser = $('.selected').attr("data-username");
  },

  ui_handlers: function() {
    var self = this;
    self.get_current_username();
    self.update_conversation();

    // user selection
    p.userList.on("click touchstart", function(e) {

      $('.selected').removeClass('selected');

      if ($(e.target).prop("tagName") == 'LI') {
        $(e.target).toggleClass("selected");
      } else {
        $(e.target).parents("li").toggleClass("selected");
      }

      self.get_current_username();
      self.update_conversation();
    });


    // check for content
    $("#enter_message").on('keyup', function(event) {

      var content = $(this).val();

      if(content.replace(/\s/g, "").length > 0) {
        $("#submit_message").addClass("has_content");
        p.hasContent = true;
      } else {
        $("#submit_message").removeClass("has_content");
        p.hasContent = false;
        $("#enter_message").attr("placeholder", "Type a message...");
      }

    });

    // handle enter key
    $("#enter_message").on('keypress', function(event){
      var keycode = (event.keyCode ? event.keyCode : event.which);

      if(keycode == '13' && !event.shiftKey && p.hasContent === true) {
        event.preventDefault();
        self.send_message();
      }

      if(keycode == '13' && !event.shiftKey && p.hasContent === false) {
        event.preventDefault();
      }

    });

    // submit message click
    $("#submit_message").on('click', function() {

      if (p.hasContent === true) {
        self.send_message();
      }

    });

  },

  chat_handlers: function() {

    p.object.on('message response', function(data) {
      console.log(data);
      var div = $("<div>", {class: "message"});
      $(div).text(data.msg);

      if (data.from == p.username && data.to == p.currentUser){
        div.addClass('to');
        p.currentMessages.append(div);
      } else if (data.from == p.currentUser && data.to == p.username) {
        div.addClass('from');
        p.currentMessages.append(div);
      }

    });

  },

  send_message: function() {
    p.object.emit('message', {msg: p.messageBox.val(), to: p.currentUser, from:p.username});
    p.messageBox.val('');
  },

  update_conversation: function(){
    $("#current_conversation #current_messages").html('');
    $("#conversation_heading").html(p.currentUser);
    this.get_messages();
  },

  get_messages: function(){
    // TODO: make sure these requirements are fulfilled - ajax call with id of user to get messages from, check on server whether the user is a match with the id, then append to conversation
    // TODO: implement pagination

    var self = this;

    $.ajax({
      url: '/get_messages',
      data: {"username":p.currentUser},
      success: function(response) {
        self.display_messages(response);
      }
    });

  },

  display_messages: function(data) {
    var div;

    data = data.results;

    for (var k in data) {

      if (data.hasOwnProperty(k)) {

        var messages = data[k];

        for (var m in messages){
          if (messages.hasOwnProperty(m)) {
            console.log(messages[m].content);

            div = $("<div>", {class: "message "});
            $(div).text(messages[m].content);

            if (messages[m].from == p.username && messages[m].to == p.currentUser){
              div.addClass('to');
              p.currentMessages.append(div);
            } else if (messages[m].from == p.currentUser && messages[m].to == p.username) {
              div.addClass('from');
              p.currentMessages.append(div);
            }

          }
        }

      }

    }

  }

};

Chat.init();
