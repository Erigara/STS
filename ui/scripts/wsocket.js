reconnectionTime = 3000;
var wsocket = {};


function openConnection() {
  wsocket.socket = new WebSocket('ws://'+window.location.hostname+':'+window.location.port+'/event');
  wsocket.listeners = [];
  wsocket.requestArray = [];
  wsocket.socket.onopen = function(event) {
    console.log("Open conection!")
    wsocket.requestArray.forEach(function(request, index, array) {
      request();
    });
  };

  wsocket.socket.onerror = function(event) {
    console.log("Lost connection with server. try to reconnect...");
    setTimeout(() => openConnection(), reconnectionTime);
  };

  wsocket.socket.onclose = function(event) {
    console.log("Lost connection with server. try to reconnect...");
    setTimeout(() => openConnection(), reconnectionTime);
  };

 wsocket.socket.onmessage = function(event) {
    var message = JSON.parse(event.data);
    console.log(message);
    var header = message['header']
    var data = message['data']
    wsocket.listeners.forEach(function(listener, index, array) {
      if (header == listener.header){
        listener.execute(data)
        if (listener.type == 'promise') {
          array.splice(index, 1);
        }
      }
    });
  };
}


wsocket.sendRequest = function(header, data) {
  if (wsocket.socket.readyState != 1) {
    wsocket.requestArray.push(function () {wsocket.socket.send(JSON.stringify({"header" : header, "data" : data}));});
  }
  else{
    wsocket.socket.send(JSON.stringify({"header" : header, "data" : data}));
  }

};

wsocket.permanentSubscribe = function(header, execute, id) {
  var listener = {'header' : header, 'execute' : execute, 'type' : 'permanent', 'id' : id};
  wsocket.listeners.push(listener);
};

wsocket.unsubscribe = function(id) {
  wsocket.listeners.forEach(function(listener, index, array) {
    if (id == listener.id){
      array.splice(index, 1);
    }
  });
};

wsocket.promiseSubscribe = function(header) {
  return new Promise(function(resolve, reject) {
    var listener = {'header' : header, 'execute' : resolve, 'type' : 'promise'};
    wsocket.listeners.push(listener);
    setTimeout(() => reject(new Error("time out")), 10000);
  });
};

wsocket.ready = function() {
  return wsocket.socket.readyState == 1
}

openConnection();
wsocket.sendRequest('handshake', {});
