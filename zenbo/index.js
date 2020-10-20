var ws = new WebSocket("ws://140.116.72.235:8080");
var time = Date($.now());
var ttt = 0;

var historyArr = [];
var historyIndex = 0;

$(window).on('load', function () {
    init();
    speechInit();
});

function init() {
    $('#mic-animation').css("display", "none");
    $('#client-content').css("display", "none");
    $('#stop-mic').css("display", "none");
    $('#chat-p-img').css("display", "none");
    $('#speech').css("display", "inherit");
    $('#server-content').css("display", "inherit");
    $('.choosen-btn').remove();
    $('#server-content').text("您好，請按下麥克風開始通話。");
}


ws.onopen = function (event) {
    //wsend("地點","raw");
}

ws.onclose = function (event) {
    console.log("Close Websocket");
};
ws.onerror = function (event) {
    if (ws.url == "ws://140.116.72.242:8080") insertServerMsg("伺服器離線中，請嘗試重新連線。",null);
}
ws.onmessage = function (event) {
    msg = JSON.parse(event.data);
    if(msg.Type != 2) historyArr.push(msg);
    historyIndex = historyArr.length-1;
    insertServerMsg(msg.Response, msg.Metadata, msg.Type);
}

function wsend(msg, type) {
    var tmp = { "DataType": type, "Data": msg };
    ws.send(JSON.stringify(tmp));
}

function insertServerMsg(msg,choosen,type) {
    if( type == 0){
        init();
        msg = (msg.replace("<b>","\""));
        msg = (msg.replace("</b>","\""));
        $('#server-content').html(msg);
        if(choosen != null){
            for (var i = 0; i < choosen.length ; i++) {
                $('<button class="choosen-btn" id=zc'+historyIndex+i+' data-opnum= '+choosen[i]+'>'+choosen[i]+'</button>').appendTo($('#zenbo-choosen'));
            }
        }else{
            $('.choosen-btn').remove();
        }
    }else if( type == 1){
        init();
        $('#server-content').css("display", "none");
        $('#chat-p-img').css("display", "inherit");
        $('#chat-p-img').attr('src') = msg;
        //$('<img src='+msg+'>').appendTo($('#chat-p'));
        console.log(msg);
    }else if(type == 2){
        window.open(msg,"開啟新分頁");
    }
}

function insertClientMsg(msg, type) {
    $('<li class="right-msg">' + msg + '</li>').appendTo($('#chatBlock'));
    if (type != 0) wsend(msg, type);
}

document.getElementById('restart').addEventListener('click', (e) => {
    document.body.requestFullscreen();
    init();
    historyArr = [];
    historyIndex = 0;
    wsend("restart","sys");
})
document.getElementById('return').addEventListener('click', (e) => { //
    if(historyIndex == 0) return;
    historyIndex -=1;
    historyArr.pop();
    console.log(historyArr);
    wsend("return","sys");
})

document.getElementById('zenbo-choosen').addEventListener('click',(e)=>{
  var clickMsg = (e.target.getAttribute('data-opnum'));
  if (clickMsg == "stop-mic" || clickMsg == null || clickMsg == "zenbo-choosen") return;
  wsend(clickMsg,"raw");
})

function restoreHistory(arrIndex){ //will have no lastChosen
    init();
    var tmp = historyArr[arrIndex];
    insertServerMsg(tmp.Response, tmp.Metadata, tmp.Type);
    var lastAns = '#zc'+arrIndex+tmp.Metadata.indexOf(historyArr[arrIndex+1].lastChosen);
    $(lastAns).css("background-color","yellow");
}

document.getElementById('last').addEventListener('click',(e)=>{
    historyIndex -= 1;
    if(historyIndex < 0) historyIndex = 0;
    restoreHistory(historyIndex);
})
document.getElementById('next').addEventListener('click',(e)=>{
    historyIndex += 1;
    if(historyIndex >= historyArr.length-1) historyIndex = historyArr.length-1;
    restoreHistory(historyIndex);
})

function changeState(nowState){
    if(nowState){ //true: to server state
        $('#mic-animation').css("display", "none");
        $('#client-content').css("display", "none");
        $('#chat-p-img').css("display", "none");
        $('#stop-mic').css("display", "none");
        $('#speech').css("display", "inherit");
        $('#server-content').css("display", "inherit");
    }else{ //false: to client state
        $('.choosen-btn').remove();
        $('#mic-animation').css("display", "inherit");
        $('#chat-p-img').css("display", "none");
        $('#client-content').css("display", "inherit");
        $('#stop-mic').css("display", "inherit");
        $('#speech').css("display", "none");
        $('#server-content').css("display", "none");
    }
}