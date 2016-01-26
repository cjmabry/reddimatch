function initialize() {
    var input = document.getElementById('pac-input');
    var autocomplete = new google.maps.places.Autocomplete(input);
    google.maps.event.addListener(autocomplete, 'place_changed', function () {
        var place = autocomplete.getPlace();
        document.getElementById('pac-input').value = place.name;
        var latitude = place.geometry.location.lat();
        var longitude = place.geometry.location.lng();

        $.ajax({
          url: '/set_location',
          data: {latitude: latitude,
          longitude: longitude}
        }).done(function() {
          console.log('location set');
        });

    });
}
google.maps.event.addDomListener(window, 'load', initialize);
