var recognition = new webkitSpeechRecognition();
var recognition, recognizing;
var speechTemp;

function speechInit() {
    if (!('webkitSpeechRecognition' in window)) {
        console.log("no speech");
    } else {
        recognizing = false;
        recognition.interimResults = false;
        recognition.continuous = false;
        recognition.lang = "cmn-Hant-TW";
    }
}


recognition.onstart = function () {
    recognizing = true;
};
recognition.onend = function () {
    insertClientMsg(speechTemp, "raw");
    recognizing = false;
    $('#client-content').text("");
    changeState(true);
};
recognition.onresult = function (event) {
    var temp = "";
    var i = event.resultIndex;
    var j = event.results[i].length - 1;
    temp = event.results[i][j].transcript;
    $('#client-content').text(temp);
    speechTemp = temp;
};


$("#speech").click(function () {
    changeState(false);
    recognition.start();
});

document.getElementById('stop-mic').addEventListener('click', (e) => {
    recognition.stop();
})
