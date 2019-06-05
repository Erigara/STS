function showWrongAuthWarning(elementId, message, time=3000) {
  var div = document.createElement('div');
  div.className = "alert alert-warning";
  div.innerHTML = message;
  var parentElem = document.getElementById(elementId);
  parentElem.insertBefore(div, parentElem.firstChild);
  setTimeout(function() {
      div.parentNode.removeChild(div);
  }, time);
}

function showSuccAuthNotify(elementId, message, time=3000) {
  var div = document.createElement('div');
  div.className = "alert alert-ok";
  div.innerHTML = message;
  var parentElem = document.getElementById(elementId);
  parentElem.insertBefore(div, parentElem.firstChild);
  setTimeout(function() {
      div.parentNode.removeChild(div);
  }, time);

}

function getFormData($form){
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function(n, i){
        indexed_array[n['name']] = n['value'];
    });
    return indexed_array;
}
