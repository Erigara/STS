function createTableSecurity(data){
  tabledata = data.tabledata;
  columns = data.columns;
  var name = findByField(columns, 'name');
  name.editor = true;
  name.validator = validateString;
  var object_id = findByField(columns, 'object_id')
  object_id.editor = smartSelectEditor;
  object_id.editorParams = {'table' : "Object", 'column' : 'object_id'};
  createAddTable(columns);
  return createTable(tabledata, columns);
}

function createTableDispatcher(data){
  tabledata = data.tabledata;
  columns = data.columns;
  var name = findByField(columns, 'name');
  name.editor = true;
  name.validator = validateString;
  var object_id = findByField(columns, 'object_id')
  object_id.editor = smartSelectEditor;
  object_id.editorParams = {'table' : "Object", 'column' : 'object_id'};
  createAddTable(columns)
  return createTable(tabledata, columns);
}

function createTableCheckpoint(data){
  tabledata = data.tabledata;
  columns = data.columns;
  var x = findByField(columns, 'x');
  x.editor = true;
  x.validator = validateNumeric;
  var y = findByField(columns, 'y');
  y.editor = true;
  y.validator = validateNumeric;
  var radius = findByField(columns, 'radius');
  radius.editor = true;
  radius.validator = validateNumeric;
  createAddTable(columns);
  return createTable(tabledata, columns);
}

function createTableMovmenthistory(data){
  tabledata = data.tabledata;
  columns = data.columns;
  createAddTable(columns);
  return createTable(tabledata, columns);
}

function createTableSensor(data){
  tabledata = data.tabledata;
  columns = data.columns;
  var mac_address = findByField(columns, 'mac_address');
  mac_address.editor = true;
  mac_address.validator = validateMac;
  var x = findByField(columns, 'x');
  x.editor = true;
  x.validator = validateNumeric;;
  var y = findByField(columns, 'y');
  y.editor = true;
  y.validator = validateNumeric;;
  var benchmark_rssi = findByField(columns, 'benchmark_rssi');
  benchmark_rssi.editor = true;
  benchmark_rssi.validator = validateNumeric;
  var benchmark_rssi_std = findByField(columns, 'benchmark_rssi_std');
  benchmark_rssi_std.editor = true;
  benchmark_rssi_std.validator = validateNumeric;
  createAddTable(columns)
  return createTable(tabledata, columns);
}

function createTableObject(data){
    tabledata = data.tabledata;
    columns = data.columns;
    var address = findByField(columns, 'address');
    address.editor = true;
    address.validator = validateNull;
    createAddTable(columns)
    return createTable(tabledata, columns);
}

function createTableRoutepoint(data) {
  tabledata = data.tabledata;
  columns = data.columns;
  var route_id = findByField(columns, 'route_id');
  route_id.editor = smartSelectEditor;
  route_id.editorParams = {'table' : "Route", 'column' : 'route_id'};
  route_id.validator = validateNull;
  var check_point_id = findByField(columns, 'check_point_id');
  check_point_id.editor = smartSelectEditor;
  check_point_id.editorParams = {'table' : "CheckPoint", 'column' : 'check_point_id'};
  check_point_id.validator = validateNull;

  var check_point_id = findByField(columns, 'check_point_id');
  check_point_id.editor = smartSelectEditor;
  check_point_id.editorParams = {'table' : "CheckPoint", 'column' : 'check_point_id'};
  check_point_id.validator = validateNull;
  var begin_time = findByField(columns, 'begin_time');
  begin_time.editor = true;
  begin_time.validator = validateTime;

  var end_time = findByField(columns, 'end_time');
  end_time.editor = true;
  end_time.validator = validateTime;
  createAddTable(columns)
  return createTable(tabledata, columns);
}

function createTableRoute(data) {
  tabledata = data.tabledata;
  columns = data.columns;
  var object_id = findByField(columns, 'object_id');
  object_id.editor = smartSelectEditor;
  object_id.editorParams = {'table' : "Object", 'column' : 'object_id'};

  var security_id = findByField(columns, 'security_id');
  security_id.editor = smartSelectEditor;
  security_id.editorParams = {'table' : "SecurityStaff", 'column' : 'security_id'};

  var dispatcher_id = findByField(columns, 'dispatcher_id');
  dispatcher_id.editor = smartSelectEditor;
  dispatcher_id.editorParams = {'table' : "DispatcherStaff", 'column' : 'dispatсher_id'};
  createAddTable(columns);
  return createTable(tabledata, columns);
}
