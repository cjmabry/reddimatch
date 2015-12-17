var properties, Chat = {
  properties : {
      url : 'http://' + document.domain + ':' + location.port,
      username: null,
      socketObject: null,
      userList: $("ul#user_list"),
      currentUser : null,
      currentUserDiv: null,
      currentUserAvatar: null,
      currentUserStatus: null,
      currentUserMatchType: null,
      messageBoxHasContent: false,
      messageBox: $("#enter_message"),
      currentMessages: $("#current_messages")
  },

  init: function() {
    p = this.properties;
    p.userList.children(':first').addClass('selected');
    this.connect();

    if ($(p.userList).has("li").length > 0) {
      this.ui_handlers();
      this.chat_handlers();

      var self = this;

      users = {};

      $(p.userList).each( function() {
        $(this).find('li').each(function() {
          var user = $(this).attr('data-username');
          users[user] = '';
        });
      });
      self.is_online(users)
    }

  },

  connect: function() {
    p.socketObject = io.connect(p.url);
    this.set_username();
  },

  set_username: function() {
    $.get("/get_username", function(data) {
        p.username = data.username;
    });
  },

  get_current_username: function() {
    p.currentUser = $('.selected').attr("data-username");
    p.currentUserMatchType = $('.selected').attr("data-match-type");
    p.currentUserDiv = $('.selected');
  },

  ui_handlers: function() {
    var self = this;
    self.get_current_username();
    self.get_avatar(300);
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
      self.get_avatar(300);
      self.update_conversation();
    });


    // check for content
    $("#enter_message").on('keyup', function(event) {

      var content = $(this).val();

      if(content.replace(/\s/g, "").length > 0) {
        $("#submit_message").addClass("has_content");
        p.messageBoxHasContent = true;
      } else {
        $("#submit_message").removeClass("has_content");
        p.messageBoxHasContent = false;
        $("#enter_message").attr("placeholder", "Type a message...");
      }

    });

    // handle enter key
    $("#enter_message").on('keypress', function(event){
      var keycode = (event.keyCode ? event.keyCode : event.which);

      if(keycode == '13' && !event.shiftKey && p.messageBoxHasContent === true) {
        event.preventDefault();
        self.send_message();
      }

      if(keycode == '13' && !event.shiftKey && p.messageBoxHasContent === false) {
        event.preventDefault();
      }

    });

    // submit message click
    $("#submit_message").on('click', function() {

      if (p.messageBoxHasContent === true) {
        self.send_message();
      }

    });

  },

  chat_handlers: function() {

    var scroll, self = this;

    p.socketObject.on('message response', function(data) {

      var div = $("<div>", {class: "message"});
      $(div).text(data.msg);

      if (data.from == p.username && data.to == p.currentUser && data.match_type == p.currentUserMatchType){
        scroll = self.is_scrolled();
        div.addClass('to');
        p.currentMessages.append(div);
        p.currentMessages.removeClass('empty');

        if(scroll) {

          self.scroll_to_bottom(true);

        }

      } else if (data.from == p.currentUser && data.to == p.username && data.match_type == p.currentUserMatchType) {
        scroll = self.is_scrolled();
        div.addClass('from');
        p.currentMessages.append(div);
        p.currentMessages.removeClass('empty');

        if(scroll) {

          self.scroll_to_bottom(true);

        }
      }

    });

  },

  send_message: function() {
    p.socketObject.emit('message', {msg: p.messageBox.val(), to: p.currentUser, from:p.username, match_type:p.currentUserMatchType});
    p.messageBox.val('');
  },

  update_conversation: function(){
    $("#current_conversation #current_messages").html('');
    $("#conversation_heading").html(p.currentUser);
    this.get_messages();
    this.get_user_info(p.currentUser, p.currentUserMatchType);
  },

  get_messages: function(){
    // TODO make sure these requirements are fulfilled - ajax call with id of user to get messages from, check on server whether the user is a match with the id, then append to conversation
    // TODO implement pagination
    // TODO implement timestamps

    var self = this;

    console.log(p.currentUserMatchType)

    $.ajax({
      url: '/get_messages',
      data: {"username":p.currentUser,"match_type":p.currentUserMatchType},
      success: function(response) {
        if(response == 'no_messages' || response == 'request' || response == 'unconfirmed') {
          self.display_prompt(response);
        } else {
          self.display_messages(response);
          self.scroll_to_bottom(false);
        }
      }
    });

  },

  display_prompt: function(type) {
    div = $("<div>", {class: "prompt"});

    if(type == 'no_messages') {
      $(div).html('<div class="prompt_icon"></div><h2><small>Go ahead, say hello!</small></h2>');
      p.currentMessages.addClass('empty');
    } else if (type == 'request') {

      div.html(
        "<div class='prompt_icon'></div><h2><small>This user has requested to match with you! Accept their match if you'd like to chat.</small></h2>" +
        "<div class='match'>" +
          "<div class='match_button'>" +
            "<span class='check glyphicon glyphicon-ok yes-match' role='button' data-username='"+ p.currentUser + "' data-match-type=" + p.currentUserMatchType + "'>" +
            "</span>" +
            "<span class='text'>Match</span>" +
            "<span class='cross glyphicon glyphicon-remove no-match' role='button' data-username='"+ p.currentUser +"' data-match-type=" + p.currentUserMatchType + "'>" +
            "</span>" +
          "</div>" +
      "</div>");

      p.currentMessages.addClass('request');
    } else if (type=='unconfirmed') {
      $(div).html('<div class="prompt_icon"></div><h2><small>This user hasn\'t accepted your match yet. You\'ll be able to chat with them once they do.</small></h2>');
      p.currentMessages.addClass('unconfirmed');
    }

    p.currentMessages.html(div);
    $("span.yes-match").on("click", function() {
      var match_username = $(this).attr("data-username");
      var match_type = p.currentUserMatchType;
      console.log(match_username)
      console.log(match_type)
      match(this, match_username, match_type);
    });

    $("span.no-match").on("click", function() {
      var match_username = $(this).attr("data-username");
      var match_type = p.currentUserMatchType;
      no_match(this, match_username, match_type);
      p.currentMessages.addClass('rejected');
      p.currentUserDiv.addClass('rejected');
    });

  },

  get_last_message: function(data) {

  },

  get_avatar: function(size) {
    $.ajax({
      url: '/get_avatar',
      data: {"username":p.currentUser,"size":size},
      success: function(response) {
        p.currentUserAvatar = response;
      }
    });
  },

  get_user_info: function(username, match_type) {
    var self = this;
    // ajax request with username, return json object with all user info
    $.ajax({
      url: 'get_user_info',
      data: {"username":username,
      match_type: match_type
    },
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

    if (data.gender !== 'None' || data.gender !== null) {
      gender = data.gender;
    } else {
      gender = "";
    }

    if (data.location !== null) {
      location = data.location;
    } else {
      location = "";
    }

    if (data.avatar !== null) {
      avatar = data.avatar;
    } else {
      avatar= "http://www.gravatar.com/?d=mm";
    }

    user_info_div = $("<div class='card current_user'><div class='profile_photo'><img src='"+ avatar +"'></div><div class='info'><div class='wrapper'><span id='conversation_heading' class='username'> " + p.currentUser + " </span><span class='age'>" + age + " </span><span class='gender'> " + gender + " </span><span class='location'> " + location + " </span></div></div></div>");

    fav_subs = $("<div>", {class:'favorite_subs'});

    if (data.fav_subs && data.fav_subs.length > 0) {

      for(var i=0; i < data.fav_subs.length; ++i) {
        if(i in data.fav_subs) {
          $(fav_subs).append(" <span class='badge'><a href='https://reddit.com/r/" + data.fav_subs[i] + "'>/r/" + data.fav_subs[i] + "</a></span> ");
        }
      }

      favorite_subs_div = $("<div class='card'><h5>Favorite Subreddits</h5></div></div>");

      favorite_subs_div.append(fav_subs);

    }

    $("#user_info").html(user_info_div);
    $("#user_info").append(favorite_subs_div);

    if(data.bio) {
      bio_div = $("<div class='card'><h5>Bio</h5></div></div>");
      $("#user_info").append(bio_div);
      bio_div.append(data.bio);
    }

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

  is_online: function(users) {
    var self = this;
    $.ajax({
      type:'POST',
      url:'is_online',
      data: JSON.stringify(users),
      dataType: 'json',
      contentType: 'application/json; charset=utf-8',
      success: function(users){
        self.set_online(users);
      }
    });
  },

  set_online: function(users){
    for(var user in users){
      if(users.hasOwnProperty(user)){
        if(users[user] == true) {
          p.userList.find("[data-username='" + user + "']").addClass('online');
        } else {
          p.userList.find("[data-username='" + user + "']").addClass('offline');
        }
      }
    }
  },

  sort_list: function(by) {

    list = $('ul#user_list');
    items = $('ul#user_list > li');

    for (var i = 0, arr = ['request', 'accepted', 'unconfirmed']; i < arr.length; i++) {
        for (var j = 0; j < items.length; j++) {
            if ($(items[j]).hasClass(arr[i]))
                list.append(items[j]);
        }
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

            div = $("<div>", {class: "message "});
            $(div).text(messages[m].content);

            if (messages[m].from == p.username && messages[m].to == p.currentUser && messages[m].match_type == p.currentUserMatchType){
              div.addClass('to');
              p.currentMessages.append(div);
            } else if (messages[m].from == p.currentUser && messages[m].to == p.username && messages[m].match_type == p.currentUserMatchType) {
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
