// TODO notifications
// TODO mobile formatting
// TODO address broken pipes
// TODO (secondary) notify user on new message if scrolled
// TODO (secondary) if no messages, prompt user to say hello
// TODO (secondary) handle no matches
// TODO (secondary) hover status icon to reveal offline or online
// TODO (secondary) get last message from user to display on user list
// TODO (secondary) auto expand text box on type
// TODO (secondary) improve online/offline (if we can't use socket, do all in one request instead of one username at a time)

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

    var self = this;

    $(p.userList).each( function() {
      $(this).find('li').each(function() {
        var user = $(this).attr('data-username');
        self.is_online(user);
      });
    });

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

    var scroll, self = this;

    p.object.on('message response', function(data) {

      console.log(data);
      var div = $("<div>", {class: "message"});
      $(div).text(data.msg);

      if (data.from == p.username && data.to == p.currentUser){
        scroll = self.is_scrolled();
        div.addClass('to');
        p.currentMessages.append(div);

        if(scroll) {

          self.scroll_to_bottom(true);

        }

      } else if (data.from == p.currentUser && data.to == p.username) {
        scroll = self.is_scrolled();
        div.addClass('from');
        p.currentMessages.append(div);

        if(scroll) {

          self.scroll_to_bottom(true);

        }
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
    this.get_user_info(p.currentUser);
  },

  get_messages: function(){
    // TODO make sure these requirements are fulfilled - ajax call with id of user to get messages from, check on server whether the user is a match with the id, then append to conversation
    // TODO implement pagination
    // TODO implement timestamps

    var self = this;

    $.ajax({
      url: '/get_messages',
      data: {"username":p.currentUser},
      success: function(response) {
        self.display_messages(response);
        self.scroll_to_bottom(false);
      }
    });

  },

  get_last_message: function(data) {

  },

  get_user_info: function(username) {
    var self = this;
    // ajax request with username, return json object with all user info
    $.ajax({
      url: 'get_user_info',
      data: {"username":username},
      success: function(response){
        self.update_user_info(response);
      }
    });
  },

  update_user_info: function(data) {
    // parse user info, create div, append it.
    var user_info_div, fav_subs, favorite_subs_div, age, gender, location;

    if (data.age !== null) {
      age = "Age: " + data.age;
    } else {
      age = "";
    }

    if (data.gender !== 'None') {
      gender = data.gender;
    } else {
      gender = "";
    }

    if (data['location'] !== null) {
      location = data['location'];
    } else {
      location = "";
    }

    user_info_div = $("<div class='card current_user'><div class='profile_photo'></div><div class='info'><div class='wrapper'><span id='conversation_heading' class='username'> " + p.currentUser + " </span><span class='age'>" + age + " </span><span class='gender'> " + gender + " </span><span class='location'> " + location + " </span></div></div></div>");

    fav_subs = $("<div>", {class:'favorite_subs'});

    for(var i=0; i<data.fav_subs.length; ++i) {
      if(i in data.fav_subs) {
        $(fav_subs).append(" <span class='badge'><a href='https://reddit.com/r/" + data.fav_subs[i] + "'>/r/" + data.fav_subs[i] + "</a></span> ");
      }
    }

    favorite_subs_div = $("<div class='card'><h5>Favorite Subreddits</h5></div></div>");

    favorite_subs_div.append(fav_subs);

    $("#user_info").html(user_info_div);
    $("#user_info").append(favorite_subs_div);

  },

  is_scrolled: function() {
    if(p.currentMessages[0].scrollHeight - p.currentMessages[0].offsetHeight == p.currentMessages.scrollTop()) {
      return true;
    }
  },

  scroll_to_bottom: function(animate) {
    if (animate) {
      $(p.currentMessages).animate({ scrollTop: $(p.currentMessages).prop("scrollHeight")}, 500);
    } else {
      p.currentMessages.scrollTop($(p.currentMessages)[0].scrollHeight);
    }
  },

  is_online: function(user) {
    var self = this;
    // check if user is online
    // ajax to server
    // check if online server side
    // return true or false
    // set appropriate class on user
    $.ajax({
      url: 'is_online',
      data: {username:user},
      success: function(response){
        self.set_online(response , user);
      }
    });
  },

  set_online: function(response, user){
    if(response == 'true') {
      p.userList.find("[data-username='" + user + "']").addClass('online');
    } else {
      p.userList.find("[data-username='" + user + "']").addClass('offline');
    }
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
