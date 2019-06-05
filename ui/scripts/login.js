var loginTime = 1000;
var warningTime = 5000;
var loginMessageS = "<strong>Успех!</strong> Вы успешно авторизированы.";
var loginMessageW = "<strong>Ошибка!</strong> Введен не правильный логин/пароль.";

$("#loginModalContent").on( "submit", function(event) {
  data = getFormData($("#loginModalContent"))
  wsocket.promiseSubscribe('login').then(
    function(result){
      success = result.success;
      if (success) {
        showSuccAuthNotify('loginModalContent', loginMessageS, loginTime);
        loginInSystem(result);
        setTimeout(function() {
            hideLoginModal();
        }, loginTime);
        on();
      }
      else {
        showWrongAuthWarning('loginModalContent', loginMessageW, warningTime);
      }
    },
    function(error) {
      console.log(error);
    }
  );
  wsocket.sendRequest('login', data);

  event.preventDefault();
  return false;
});

function displayLoginModal() {
  document.getElementById('loginModal').style.display='block';
}

function hideLoginModal() {
  document.getElementById('loginModal').style.display='none';
}

function loginButtonOn() {
  var button = $("#loginButton")[0];

  button.innerHTML = "Выйти из системы";
}
function loginButtonOff(){
  var button = $("#loginButton")[0];
  button.innerHTML = "Войти в систему";
}

$("#loginForm").on( "submit", function(event) {
  if (!checkAuthentication()){
    displayLoginModal();
  }
  else {
    logoutOfSystem();
    off();
  }
  event.preventDefault();
  return false;
});

function loginInSystem(data) {
    status = data.status;
    setCookie('status', status);
}

function logoutOfSystem() {
  setCookie("status", "");
}

function checkAuthentication() {
  return getCookie('status') != "";
}

function getUserStatus() {
  return getCookie('status');
}

function blockContent() {
  document.getElementById('overlay').style.display='block';
}

function unblockContent() {
  document.getElementById('overlay').style.display='none';
}

function on() {
  loginButtonOn();
  unblockContent();
  startMonitoring();
  startNotifications();
}

function off() {
  loginButtonOff();
  blockContent();
  stopMonitoring();
}

if (checkAuthentication()) {
    on();
}
else {
    off();
}
