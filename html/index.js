var ws = new WebSocket("ws://140.116.72.235:8080");
var time = Date($.now());
var scro;
var serverHistory = [];

$(window).on('load', function () {
    init();
});
function init() {
    scro = $("#chat").mCustomScrollbar();
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
    insertServerMsg(msg.Response, msg.Metadata, msg.Type);
    /*
    var res = (msg.Response).split("sys_");
    var metadata = msg.Metadata;
    if (res.length != 1) { //sys 1. history 2. token
        if (res[1] == "history") restoreHistory(metadata);
        if (res[1] == "token") $.cookie('token', metadata, { expires: 7, path: '/' });
    } else { // 1. one-line 2. list
        if (!metadata) { // is link?
            if (((res[0].split("http")).length > 1)) {
                insertServerMsg(res[0], 1);
                return;
            }
            insertServerMsg(res[0], 0);
        } else {
            insertServerMsg(res[0], metadata);
        }
    }*/
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
//<ul id="chatBlock" class="rounded-messages messages-width-large">
function insertServerMsg(msg, chosen, type) {
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

    } else if (type == 2) {
        window.open(msg, "開啟新分頁");
    }
    serverHistory.push(res);
    $(res).appendTo($('#chatBlock'));
    updateScrollbar();
}
function insertClientMsg(msg, type) {
    serverHistory == null ? len = 0 : len = serverHistory.length;
    serverHistory.push('<li id="p' + len + '" class="right-msg">' + msg + '</li>');
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
    } else if (clickMsg == "start") {
        insertClientMsg("開始", 0);
        wsend("start", "sys");
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
    }
})

function lastStep() {
    $('#p' + (serverHistory.length - 1)).remove();
    serverHistory.pop();
    $('#p' + (serverHistory.length - 1)).remove();
    serverHistory.pop();
    wsend("return", "sys");
}
