var contentTable;
var tableName;

function showEditModal() {
  if (getUserStatus() != 'admin') {
    alert("Не достаточно прав доступа!");
  }
  else {
    document.getElementById('editModal').style.display='block';
  }
}


function getTableSelect() {
  var table = $("#ddlTableSelect").children("option:selected").val();
  return table;
}

$("#editModalContent").on( "submit", function(event) {
  tableName = getTableSelect();
  wsocket.promiseSubscribe("get_data").then(
    function(data){
      switch (tableName) {
        case "SecurityStaff":
          contentTable = createTableSecurity(data);
          break;
        case "DispatcherStaff":
            contentTable = createTableDispatcher(data);
            break;
        case "CheckPoint":
            contentTable = createTableCheckpoint(data);
            break;
        case "MovmentHistory":
            contentTable = createTableMovmenthistory(data);
            break;
        case "Sensor":
            contentTable = createTableSensor(data);
            break;
        case "Object":
            contentTable = createTableObject(data);
            break;
        case "RoutePoint":
            contentTable = createTableRoutepoint(data);
            break;
        default:

      }
    },
    function(error) {
      console.log(error);
    }
  );
  wsocket.sendRequest('get_data', {'table' : tableName});
  return false;
});



function createTable(tabledata, columns){
  columns.forEach(function(elem, index, array) {
    elem.headerFilter="input";
  });
  var table = new Tabulator("#dataTable", {
    selectable:true,
    selectablePersistence:false,
  	data:tabledata,           //load row data from array
  	layout:"fitColumns",      //fit columns to width of table
  	responsiveLayout:"hide",  //hide columns that dont fit on the table
  	tooltips:true,            //show tool tips on cells
  	addRowPos:"top",          //when adding a new row, add it to the top of the table
  	history:false,             //allow undo and redo actions on the table
  	pagination:"local",       //paginate the data
  	paginationSize:10,         //allow 7 rows per page of data
  	movableColumns:true,      //allow column order to be changed
  	resizableRows:true,       //allow row order to be changed
  	columns: columns          //define the table columns
  });
  return table;
}

function findByField(columns, field) {
  var column = {};
  columns.forEach(function(elm, index, array) {
      if (field == elm.field) {
        column = elm;
        return;
      }
  });
  return column;
}

function createTableSecurity(data){
  tabledata = data.tabledata;
  columns = data.columns;
  var name = findByField(columns, 'name');
  name.editor = true;
  var object_id = findByField(columns, 'object_id')
  object_id.editor = "select";
  object_id.editorParams= {values:["None",]};
  return createTable(tabledata, columns);
}

function createTableDispatcher(data){
  tabledata = data.tabledata;
  columns = data.columns;
  var name = findByField(columns, 'name');
  name.editor = true;
  var object_id = findByField(columns, 'object_id')
  object_id.editor = "select";
  object_id.editorParams= {values:["None",]};
  return createTable(tabledata, columns);
}

function createTableCheckpoint(data){
  tabledata = data.tabledata;
  columns = data.columns;
  var x = findByField(columns, 'x');
  x.editor = true;
  x.validator = "float";
  var y = findByField(columns, 'y');
  y.editor = true;
  y.validator = "float";
  var radius = findByField(columns, 'radius');
  radius.editor = true;
  radius.validator = "float";
  return createTable(tabledata, columns);
}

function createTableMovmenthistory(data){
  tabledata = data.tabledata;
  columns = data.columns;
  return createTable(tabledata, columns);
}

function createTableSensor(data){
  tabledata = data.tabledata;
  columns = data.columns;
  var sensor_id = findByField(columns, 'sensor_id');
  sensor_id.editor = true;
  sensor_id.validator = ["required", "regex:^[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}$"];
  var x = findByField(columns, 'x');
  x.editor = true;
  x.validator = "float";
  var y = findByField(columns, 'y');
  y.editor = true;
  y.validator = "float";
  var benchmark_rssi = findByField(columns, 'benchmark_rssi');
  benchmark_rssi.editor = true;
  benchmark_rssi.validator = "float";
  return createTable(tabledata, columns);
}

function createTableObject(data){
    tabledata = data.tabledata;
    columns = data.columns;
    var address = findByField(columns, 'address');
    address.editor = true;
    address.validator = "string";
    return createTable(tabledata, columns);
}

function createTableRoutepoint(data) {
  tabledata = data.tabledata;
  columns = data.columns;

  var check_point_id = findByField(columns, 'check_point_id');
  check_point_id.editor = "select";
  check_point_id.editorParams = {'values' : ["None",]};
  check_point_id.validator = "required";
  function validateTime(cell, value, parameters) {
    var isValid = /^([0-1]?[0-9]|2[0-4]):([0-5][0-9])(:[0-5][0-9](\.[0-9]+)?)?$/.test(value);
    return isValid;
  }
  var begin_time = findByField(columns, 'begin_time');
  begin_time.editor = true;
  begin_time.validator = ["required", { type : validateTime, parameters:{}}];

  var end_time = findByField(columns, 'end_time');
  end_time.editor = true;
  end_time.validator = ["required", { type : validateTime, parameters:{}}];
  return createTable(tabledata, columns);
}

function addRow() {
  contentTable.addRow({});
}
function deleteSelectedRows() {
  var selectedRows = contentTable.getSelectedRows();
  var selectedData = contentTable.getSelectedData();
  wsocket.promiseSubscribe("delete_data").then(
    function(data){
        if (data.success) {
          for(var i=0;i<selectedRows.length;i++) {
            selectedRows[i].delete();
          }
        }
        else {
          console.log("Can't delete data...");
        }
    },
    function(error) {
      console.log(error);
  });
  wsocket.sendRequest('delete_data', {'table' : tableName, 'rows' : selectedData});
}
