function getColumnFromTable(table, column, ddl) {
  let values = []
  var option = document.createElement("option");
  option.text = `id : None`;
  option.value = 'None';
  ddl.appendChild(option);

  wsocket.promiseSubscribe("get_column").then(
    function(data){
        data.column.forEach( function(elem, index, array) {
          var option = document.createElement("option");
          option.text = `id : ${elem[column]}`;
          option.value = elem[column];
          ddl.appendChild(option);
          values.push(elem[column]);
        });
    },
    function(error) {
      console.log(error);
    }
  );
  wsocket.sendRequest('get_column', {'table' : table, 'column' : column});
  return values;
}


var smartSelectEditor = function(cell, onRendered, success, cancel, editorParams){
    //cell - the cell component for the editable cell
    //onRendered - function to call when the editor has been rendered
    //success - function to call to pass the successfuly updated value to Tabulator
    //cancel - function to call to abort the edit and return to a normal cell
    //editorParams - params object passed into the editorParams column definition property

    //create and style editor
    var editor = document.createElement("select");
    getColumnFromTable(editorParams.table, editorParams.column, editor);


    //create and style input
    editor.style.padding = "3px";
    editor.style.width = "100%";
    editor.style.boxSizing = "border-box";

    //set focus on the select box when the editor is selected (timeout allows for editor to be added to DOM)
    onRendered(function(){
        editor.focus();
        editor.style.css = "100%";
    });

    //when the value has been set, trigger the cell to update
    function successFunc(){
        success(editor.options[editor.selectedIndex].value);
    }

    editor.addEventListener("change", successFunc);
    editor.addEventListener("blur", successFunc);

    //return the editor element
    return editor;
};
