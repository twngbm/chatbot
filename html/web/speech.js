var recognition, recognizing;
function speechInit() {
    if (!('webkitSpeechRecognition' in window)) {
        console.log("no speech");
    } else {
        recognizing = false;
        recognition = new webkitSpeechRecognition();
        recognition.lang = "cmn-Hant-TW";
        recognition.continuous = false;
    }
    if (recognizing) {
        console.log("speech stop");
        recognition.stop();
    } else {
        console.log("speech start");
        recognition.start();
    }
    recognition.onresult = function (event) {
        var temp = "";
        for (var i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                temp += event.results[i][0].transcript;
            }
        }
        console.log(temp);
        console.log(event);
        insertMessage(temp);
    };

    recognition.onstart = function () {
        recognizing = true;
        console.log(recognition);
    };
    recognition.onend = function () {
        recognizing = false;
    };
}

var onSpeech = new Boolean(false);
$("#speech").click(function(){
    console.log($("#speech").attr("src"));
    if(!onSpeech){
        $("#speechPic").attr("src","img/mic-animate.gif");
    }else{
        $("#speechPic").attr("src","img/mic.gif");
    }
    onSpeech = !onSpeech;
    console.log(onSpeech);
    speechInit();
});
