var contentTable;
var addTable;
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
        case "Route":
            contentTable = createTableRoute(data);
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
    cellEdited: updateRow,
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

function createAddTable(columns){
  var table = new Tabulator("#addTable", {
    selectablePersistence:false,
  	layout:"fitColumns",      //fit columns to width of table
  	responsiveLayout:"hide",  //hide columns that dont fit on the table
  	tooltips:true,            //show tool tips on cells
  	addRowPos:"top",          //when adding a new row, add it to the top of the table
  	history:false,             //allow undo and redo actions on the table
  	movableColumns:true,      //allow column order to be changed
  	resizableRows:true,       //allow row order to be changed
  	columns: columns          //define the table columns
  });
  table.addRow({});
  addTable = table;
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

function updateRow(row){
  var rowData = row.getData();
  wsocket.promiseSubscribe("modify_data").then(
    function(data){
        if (data.success) {
          showSuccAuthNotify('editModalContent', 'Данные успешно обновлены');
        }
        else {
          showWrongAuthWarning('editModalContent', 'Произошла ошибка при обновлении данных');
        }
    },
    function(error) {
      console.log(error);
  });
  wsocket.sendRequest('modify_data', {'table' : tableName, 'row' : rowData});
}

function addRow() {
  let row = addTable.getRows()[0];
  let rowData = row.getData();
  let isValid = true;
  // не учитывает незаполняемые поля id;
  let i = 0;
  for (key in rowData) {
      if(!rowData[key] && i != 0) {
          isValid = false;
      }
      i += 1;
  }
  if(isValid) {
    wsocket.promiseSubscribe("add_data").then(
      function(data){
          if (data.success) {
            clearAddRow();
            contentTable.addRow(data.row);
            showSuccAuthNotify('editModalContent', 'Данные успешно добавлены');
          }
          else {
            showWrongAuthWarning('editModalContent', 'Произошла ошибка при добавлении данных');
          }
      },
      function(error) {
        console.log(error);
    });
    wsocket.sendRequest('add_data', {'table' : tableName, 'row' : rowData});
  }
  else {
    showWrongAuthWarning('editModalContent', 'Указаны некорректные данные');
  }
}

function clearAddRow() {
  let row = addTable.getRows()[0];
  row.delete();
  addTable.addRow({});
}
