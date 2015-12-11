var button = document.getElementById('update-button'), label = document.getElementById('update-button-label'), initialValues = {}, fields = document.getElementsByClassName('field');

button.disabled = true;

for (var i = 0; i < fields.length; i++) {

  initialValues[$(fields[i]).children()[1].getAttribute('id')] = $(fields[i]).children()[1].value;

}

console.log(initialValues);

$(fields).on('keyup', function() {
    console.log($(this).children()[1].value);

    if($(this).children()[1].value != initialValues[$(this).children()[1].getAttribute('id')]) {
      $(label).removeClass('disabled');
      button.disabled = false;
    } else {
      $(label).addClass('disabled');
      button.disabled = true;
    }

});
