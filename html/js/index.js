//from index.js
var ws = new WebSocket("ws://140.116.72.242:8080"); 
var pic = "img/messageImage_1596638102086.jpg";
var token ;
ws.onopen = function(event) {
	token = $.cookie("token");
	if( !token ){ws.send("sys_newconversation")}
	else{ws.send(("sys_token_") + $.cookie("token"))}
}
ws.onerror = function(event) {
    console.log("error");
    getMessage("伺服器離線中，請嘗試重新連線。");
    //location.reload();
}
ws.onmessage = function(event)  { 
    var message_received = event.data;
	if(!token){
		if( message_received.includes("sys_")) $.cookie("token", message_received.split("sys_token_")[1] , {expires: 3});
		return;
	}
    getMessage(message_received);
};

var $messages = $('.messages-content'),
    d, h, m;

$(window).load(function() {
    $messages.mCustomScrollbar();
});

function updateScrollbar() {
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

function insertMessage(mes) {
    var msg;
    if(mes){
        msg = mes;
    }else{
        msg = $('.message-input').val();
        //ws.send(msg);
    }
	ws.send(msg);
    if ($.trim(msg) == '') {
        return false;
    }
    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();
    $('<div class="message loading new"><figure class="avatar"><img src="'+pic+'" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
}

$('.message-submit').click(function() {
    insertMessage();
});

$(window).on('keydown', function(e) {
    if (e.which == 13) {
        insertMessage();
        return false;
    }
})

function getMessage(mes){
    $('.message.loading').remove();
    $('<div class="message new"><figure class="avatar"><img src="'+pic+'" /></figure>' + mes + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    updateScrollbar();
}

var recognition, recognizing;
function speechInit(){
	if(!('webkitSpeechRecognition' in window)){
		console.log("no speech");
	}else{
		recognizing = false;
		recognition = new webkitSpeechRecognition();
		recognition.lang="cmn-Hant-TW";
		recognition.continuous = false;
	}
	if(recognizing){
		console.log("speech stop");
		recognition.stop();
	}else{
		console.log("speech start");
		recognition.start();
	}
	recognition.onresult = function(event){
		var temp = "";
		for( var i = event.resultIndex; i < event.results.length; ++i){
			if(event.results[i].isFinal){
				temp += event.results[i][0].transcript;
			}
		}
		console.log(temp);
		console.log(event);
		insertMessage(temp);
	};

	recognition.onstart = function(){
		recognizing = true;
		console.log(recognition);
	};
	recognition.onend = function(){
		recognizing = false;
	};
}

$("#speech").click(function(){
	console.log("start to speech recognition");
	speechInit();
});

$("#speechStop").click(function(){
	console.log("stop");
	recognition.stop();
});

