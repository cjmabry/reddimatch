if ("geolocation" in navigator) {
  navigator.geolocation.getCurrentPosition(function(position) {
    console.log(position.coords.latitude + ' ' + position.coords.longitude);
    $.ajax({
      url: '/set_location',
      data: {latitude: position.coords.latitude,
      longitude: position.coords.longitude}
    }).done(function() {
      console.log('location set');
    });
  });
} else {
  /* geolocation IS NOT available */
}
