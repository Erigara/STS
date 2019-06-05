var registerTime = 1000;
var warningTime = 5000;
var registerMessageS = "<strong>Успех!</strong> Пользователь зарегистрирован.";
var registerMessageW = "<strong>Ошибка!</strong> Введенный login занят.";



function showRegisterModal() {
  if (getUserStatus() != 'admin') {
    alert("Не достаточно прав доступа!");
  }
  else {
    document.getElementById('registerModal').style.display='block';
  }
}
$("#registerModalContent").on( "submit", function(event) {
  data = getFormData($("#registerModalContent"))
  if (data.admin == "on") {
    data.admin = true;
  }
  else {
    data.admin = false;
  }
  wsocket.promiseSubscribe('register').then(
    function(result){
      success = result.success;
      if (success) {
        showSuccAuthNotify('registerModalContent', registerMessageS, registerTime);
        setTimeout(function() {
            document.getElementById('registerModal').style.display='none';
        }, registerTime);
      }
      else {
        showWrongAuthWarning('registerModalContent', registerMessageW, warningTime);
      }
    },
    function(error) {
      console.log(error);
    }
  );
  wsocket.sendRequest('register', data);

  event.preventDefault();
  return false;
});
