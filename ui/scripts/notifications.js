const notificationId = 'notification';

function startNotifications() {
    wsocket.permanentSubscribe('raise_warning', raise_warning, notificationId);
};

function stopNotifications() {
  wsocket.unsubscribe(notificationId);
}

function createNotification(message) {
  var notification = document.createElement('div');
  notification.className = 'alert alert-warning';
  notification.innerHTML = message;
  cancelButton = document.createElement('span');
  cancelButton.className = 'close';
  cancelButton.innerHTML = '&times;'
  cancelButton.addEventListener('click', function() {
    if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
  });
  notification.insertBefore(cancelButton, notification.firstChild);
  return notification
}

function appendToNotificationTray(div) {
  var parentElem = document.getElementById('notificationTray');
  parentElem.insertBefore(div, parentElem.firstChild);
}

function raise_warning(data) {
    var message = `Сотрудник: ${data.security_id} отклонился от маршрута №${data.route_id} в ${data.time}`
    var notification = createNotification(message);
    appendToNotificationTray(notification);
}
