function initialize() {

  console.log($('#location'));

    if($('#disable_location')[0].checked === true) {
      $('.location-criteria').hide(500, function() {});
      enable_form();
    } else {
      if(!$('#location')[0].value) {
        disable_form();
      }
    }

    $('#disable_location').on('change', function (){
      if($('#disable_location')[0].checked === true) {
        enable_form();
        $('.location-criteria').slideUp(500, function() {});
      } else {
        disable_form();
        $('.location-criteria').slideDown(500, function() {});
      }
    });

    var input = document.getElementById('location');
    var autocomplete = new google.maps.places.Autocomplete(input, 'regions');

    function set_place() {
      remove_classes();

      var place = autocomplete.getPlace();

      if (place) {

        if (place.geometry) {
          var latitude = place.geometry.location.lat();
          var longitude = place.geometry.location.lng();
          document.getElementById('location').value = place.name;

          in_process();

          $.ajax({
            url: '/set_location',
            data: {latitude: latitude,
            longitude: longitude,
            location: place.name,
          }
          }).done(function() {
              was_successful(true);
          }).fail(function () {
              was_successful(false);
          });
        } else {
          was_successful(false);
        }
      } else {
        was_successful(false);
      }
    }

    $("#location").on('keypress', function (event) {

      if(event.keyCode == 13) {
        event.preventDefault();
        set_place();
      }

    });

    $("#location").on('blur', function (event) {
      set_place();
    });

    google.maps.event.addListener(autocomplete, 'place_changed', function() {
      console.log('place changed');
      set_place();
    });
}

function remove_classes() {
  $('.location-status').removeClass('in-process success failed glyphicon-refresh glyphicon-refresh-animate glyphicon-ok glyphicon-remove');
}

function was_successful(success) {
  if (success) {
    remove_classes();
    $('.location-status').addClass('success glyphicon-ok');
    enable_form();
  } else {
    disable_form();
    remove_classes();
    $('.location-status').addClass('failed glyphicon-remove');
  }
}

function in_process() {
    $('.location-status').addClass('in-process glyphicon-refresh glyphicon-refresh-animate');
}

function enable_form() {
  $('#next-button').prop("disabled", false);
}

function disable_form() {
  $('#next-button').prop("disabled", true);
}

google.maps.event.addDomListener(window, 'load', initialize);
