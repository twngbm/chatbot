var ws = new WebSocket("ws://140.116.72.242:8080");
var time = Date($.now());
var scro;
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
    if (ws.url == "ws://140.116.72.242:8080") insertServerMsg("伺服器離線中，請嘗試重新連線。", 0);
}
ws.onmessage = function (event) {

    msg = JSON.parse(event.data);
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
    }
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

function insertServerMsg(msg, md) {
    if (md == 0) {
        $('<li>' + msg + '</li>').appendTo($('#chatBlock'));
    } else if (md == 1) {
        $('<li><a href="' + msg + '" target="_blank">' + msg + '</a></li>').appendTo($('#chatBlock'));
    } else {
        var tmp = ""
        md.forEach(element => tmp += "<button data-opnum=" + element + ">" + element + "</button><br>");
        $('<ul id="chatBlock" class="rounded-messages messages-width-large"><li>' + msg + '<br>' + tmp + '</ul>').appendTo($('#chatBlock'));
    }
    updateScrollbar();
}
function insertClientMsg(msg, type) {
    $('<li class="right-msg">' + msg + '</li>').appendTo($('#chatBlock'));
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
    if (clickMsg == null) return;
    if (clickMsg == "start") {
        insertClientMsg("開始", 0);
        wsend("start", "sys");
        return;
    }
    insertClientMsg(clickMsg, "clicked");
})


document.getElementById('sys_btn').addEventListener('click', (e) => {
    var clickMsg = (e.target.getAttribute('id'));
    if (clickMsg == null) return;
    insertClientMsg(clickMsg, "sys");
})

function restoreHistory(metadata) {
    for (var i = 0; i < metadata.length; i += 1) {
        if (metadata[i][1] == "Client") insertClientMsg(metadata[i][0], 0);
        else if (metadata[i][1] == "Server") insertServerMsg(metadata[i][0], 0);
        else console.log("ERROR");
    }
}
