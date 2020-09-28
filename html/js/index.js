//from index.js
var ws = new WebSocket("ws://140.116.72.233:8000");
var pic = "img/messageImage_1596638102086.jpg";
var token;
var hasToken = false;
ws.onopen = function (event) {
    console.log("Open websocket")
}
ws.onclose=function(event){
    console.log("Close Websocket");
};
ws.onerror = function (event) {
    console.log("error");
    getMessage("伺服器離線中，請嘗試重新連線。");
}
ws.onmessage = function (event) {
    var message_received = event.data;
    
    if (message_received.includes("sys_")) {
        if (message_received.includes("sys_token_")) {
            if (message_received.includes("sys_")) $.cookie("token", message_received.split("sys_token_")[1], { expires: 3 });
            hasToken = true;
            return;
        }
        if(message_received.includes("sys_history_")){
			restoreHistory(message_received.split("sys_history_")[1]);
        }
    }
    else {
        getMessage(message_received);
    }
};

var $messages = $('.messages-content'),
    d, h, m;
console.log($messages);
$(window).load(function () {
    $messages.mCustomScrollbar();
    speechInit();
});

function updateScrollbar() {
    console.log($messages);
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
        m = d.getMinutes();
        $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
}

function insertMessage(mes,restore) {
    var msg;
    if (mes) {
        msg = mes;
    } else {
        msg = $('.message-input').val();
        //ws.send(msg);
    }
    
    if (!restore){
        ws.send(msg);
        if ($.trim(msg) == '') {
            return false;
        }
    }
    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();
    $('<div class="message loading new"><figure class="avatar"><img src="' + pic + '" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
}

$('.message-submit').click(function () {
    insertMessage();
});

$(window).on('keydown', function (e) {
    if (e.which == 13) {
        insertMessage();
        return false;
    }
})

function getMessage(mes) {
    $('.message.loading').remove();
    $('<div class="message new"><figure class="avatar"><img src="' + pic + '" /></figure>' + mes + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    updateScrollbar();
}
function restoreHistory(histString){
	histString=histString.replace("[","");
    histString=histString.replace("]","");
    histString=histString.split("'").join("");
    histString = histString.split(",");
    console.log(histString);
	for (var i = 0; i < histString.length ;i+=2){
        getMessage(histString[i]);
		insertMessage(histString[i+1],true);
	}
}


function restoreHistory(hist){
	for ( i = 0 ; i < hist.length; i+=2 ){
		insertMessage(hist[i]);
		getMessage(hist[i+1]);
	}
}

