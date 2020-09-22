var ws = new WebSocket("ws://140.116.72.233:8000");
var token;
var time = Date($.now());
var scro;

$(window).on('load',function () {
  scro = $("#chat").mCustomScrollbar();
});

function init(){
  scro = $("#chat").mCustomScrollbar();
  
}

function li_onclick(name){
  console.log(name);
}

//websocket
ws.onopen = function (event) {
    console.log("Open websocket")
}
ws.onclose=function(event){
    console.log("Close Websocket");
};
ws.onerror = function (event) {
  console.log("error");
  insertServerMsg("伺服器離線中，請嘗試重新連線。");
}
ws.onmessage = function (event) {
  var msg_json = JSON.parse(event.data);
  console.log(msg_json);
}
function wsend(msg,type){
  var tmp = {"DataType":type, "Data":msg};
  console.log(tmp);
  ws.send(tmp);
}

/*scrollbar*/
function updateScrollbar() {
  scro.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
          scrollInertia: 10,
          timeout: 0
  });
}

function insertServerMsg(msg){
  $('<li>' + msg + '</li>').appendTo($('#chatBlock'));
  updateScrollbar();
  //$('<li class="time-left">'+ getDate() + '</li>').appendTo($('#chatBlock'));
}
function insertClientMsg(msg){
  $('<li class="right-msg">' + msg + '</li>').appendTo($('#chatBlock'));
  wsend(msg,"raw");
  //ws.send(msg);
  updateScrollbar();
}

function getDate(){
  time = Date($.now()).toString();
  return Date($.now()).toString().split("GMT")[0];
}
$(document).ready(function(){
  $('#send').click(function () {
    inputMsg = $('#inputText').val();
    if(inputMsg != ""){
      insertClientMsg(inputMsg);
      $('#inputText').val(null);
    }
  });
  $(window).keydown(function(event){
    if(event.keyCode == 13) {
      event.preventDefault();
      inputMsg = $('#inputText').val();
      if(inputMsg != ""){
        insertClientMsg(inputMsg);
        $('#inputText').val(null);
      }
    }
  });
});

