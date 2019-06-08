function validateTime(cell, value, parameters) {
  var isValid = /^([0-1]?[0-9]|2[0-4]):([0-5][0-9])(:[0-5][0-9](\.[0-9]+)?)?$/.test(value);
  return isValid;
}

function validateNull(cell, value, parameters) {
  var isValid = (value != "");
  return isValid;
}

function validateNull(cell, value, parameters) {
  var isValid = (value != "");
  return isValid;
}

function validateNumeric(cell, value, parameters) {
  var isValid = /^[+-]?[0-9]+(\.[0-9]+)?$/.test(value);
  return isValid;
}

function validateMac(cell, value, parameters) {
  var isValid = /^[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}$/.test(value);
  return isValid;
}

function validateString(cell, value, parameters) {
  var isValid = /^[A-Za-zА-Яа-я ]+$/.test(value);
  return isValid;
}
