var ip = location.host;
var wss = "ws://"+ ip +":8080";
var ws = new WebSocket(wss);
var time = Date($.now());
var scro;
var serverHistory = [];

$(window).on('load', function () {
    init();
});
function init() {
    scro = $("#chat").mCustomScrollbar();
}

window.onfocus = function () {
    updateScrollbar();
}

ws.onopen = function (event) {
    console.log("Open websocket");
}

ws.onclose = function (event) {
    console.log("Close Websocket");
};
ws.onerror = function (event) {
}
ws.onmessage = function (event) {
    msg = JSON.parse(event.data);
    insertServerMsg(msg.Response, msg.Metadata, msg.Type, msg.URL);
}

function wsend(msg, type) {
    var tmp = { "DataType": type, "Data": msg };
    ws.send(JSON.stringify(tmp));
}

/*scrollbar*/
function updateScrollbar() {
    scro.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function insertServerMsg(msg, chosen, type, URL) {
    var res = "";
    serverHistory == null ? len = 0 : len = serverHistory.length;
    if (type == 0 && chosen == null) {
        res = ('<li id="p' + len + '">' + msg + '</li>');
    } else if (type == 0) {
        var btn = "";
        chosen.forEach(element => btn += "<button data-opnum=" + element + ">" + element + "</button><br>");
        btn += "<button data-opnum=restart id=cho-restart></button>";
        btn += "<button data-opnum=return id=cho-return></button><br>";
        res = ('<li id="p' + len + '">' + msg + '<br>' + btn + '</li>');
    } else if (type == 1) {
        var btn = "";
        chosen.forEach(element => btn += "<button data-opnum=" + element + ">" + element + "</button><br>");
        res += '<li id="p' + len + '"><img data-opnum="chat-p-img" src=' + msg + '><br>' + btn + '</li>'
    } else if (type == 2) {
        var btn = "";
        chosen.forEach(element => btn += "<button data-opnum=" + element + ">" + element + "</button><br>");
        btn += "<button data-opnum=restart id=cho-restart></button>";
        btn += "<button data-opnum=return id=cho-return></button><br>";
        res = ('<li id="p' + len + '">' + msg + '<br>' + btn + '</li>');
        window.open(URL, "開啟新分頁");
    }
    if (res != "") serverHistory.push(res);
    $(res).appendTo($('#chatBlock'));
    updateScrollbar();
}
function insertClientMsg(msg, type) {
    serverHistory == null ? len = 0 : len = serverHistory.length;
    serverHistory.push('<li id="p' + len + '" class="right-msg">' + msg + '</li>');
    console.log("serverHistory PUSH client side");
    console.log(serverHistory);
    $('<li id=p' + len + ' class="right-msg">' + msg + '</li>').appendTo($('#chatBlock'));
    if (type != 0) wsend(msg, type);
    updateScrollbar();
}

function getDate() {
    time = Date($.now()).toString();
    return Date($.now()).toString().split("GMT")[0];
}
$(document).ready(function () {
    $('#send').click(function () {
        inputMsg = $('#inputText').val();
        if (inputMsg != "") {
            insertClientMsg(inputMsg, "raw");
            $('#inputText').val(null);
        }
    });
    $(window).keydown(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            inputMsg = $('#inputText').val();
            if (inputMsg != "") {
                insertClientMsg(inputMsg, "raw");
                $('#inputText').val(null);
            }
        }
    });
});

document.getElementById('chatBlock').addEventListener('click', (e) => {
    var clickMsg = (e.target.getAttribute('data-opnum'));
    if (clickMsg == null) {
        return;
    } else if (clickMsg == "restart") {
        insertClientMsg(clickMsg, "sys");
        location.reload();
    } else if (clickMsg == "return") {
        lastStep();
        return;
        //insertClientMsg(clickMsg,"sys");
    } else if (clickMsg == "chat-p-img") {
        window.open((e.target.getAttribute('src')), "開啟新分頁");
        return;
    } else {
        insertClientMsg(clickMsg, "raw");
    }
})


document.getElementById('sys_btn').addEventListener('click', (e) => {
    var clickMsg = (e.target.getAttribute('id'));
    if (clickMsg == "restart") {
        insertClientMsg(clickMsg, "sys");
        location.reload();
    } else if (clickMsg == "return") {
        lastStep();
        return;
        //insertClientMsg(clickMsg, "sys");
    } else if (clickMsg == "help"){
		window.open("img/help.jpg","_blank");	
		return;	
	}
})

function lastStep() {
    $('#p' + (serverHistory.length - 1)).remove();
    serverHistory.pop();
    $('#p' + (serverHistory.length - 1)).remove();
    serverHistory.pop();
    console.log(serverHistory.length);
    if (serverHistory.length == 1) location.reload();
    wsend("return", "sys");
}
