


//window.alert('script connected')

//<!--Initiating "socket" instance connected to backend. -->


//const button = document.getElementById('sendBtn');
//
//// Add an event listener to the element
//button.addEventListener('click', function(event) {
//  console.log('Button value:', event.target.text);
//});



let input = document.getElementById('chatInput');
let sendBtn = document.getElementById('sendBtn');
let screenshotBtn = document.getElementById('screenshotBtn');
let recordBtn = document.getElementById('recordBtn');
let emojisDiv = document.getElementById('emojis');


let j = 15

if (j == (17 || 15)) {
    console.log('True')
}


//Function send messages to serever

function sendMessage(event) {

    try {

        let id = event.target.id;

        if (['take_photo', 'screenshotBtn'].includes(id)) {
            console.log(id);
            socket.send('<SCREENSHOT>');
            alert('[ <INFO> ]\nMade a ScreeShot');

        }else if (id == 'start_record') {

//            alert('[ <INVALID> ]\nThe option is under construction.');
            socket.send('<START_RECORD>')
            let recordIcon = document.getElementById(id);
            recordIcon.id = 'stop_record'
//            Change style of the record button to
            let recordBtn = document.getElementById('recordBtn');
            recordBtn.style.color = 'red';
            recordBtn.style.borderColor = 'red';

        }else if (id == 'stop_record') {

            console.log(id);
            socket.send('<STOP_RECORD>')
//            alert('Stop record');
            let recordIcon = document.getElementById(id);
            recordIcon.id = 'start_record';

            let recordBtn = document.getElementById('recordBtn');
            recordBtn.style.color = 'grey';
            recordBtn.style.borderColor = 'grey';

//            location.reload();
        }
    }
    catch(err) {}

//    let message = ($('#input').val()).replace(/\n/gi, '');
//    $('#input').val('');
//    if (message) {
//        socket.send(socket.id.slice(0, 5).toUpperCase() + ': ' + message);
//    };
    let message = ($('#chatInput').val()).replace(/\n/gi, '');

    $('#chatInput').val('');
    if (message) {
        socket.send(message);
    };
};

// Send message on "Enter" key pressed

input.addEventListener('keypress', function(event) {
    if (event.key == 'Enter') {
        sendMessage();
    };
});

// Send message on "Send" button pressed

sendBtn.addEventListener('click', sendMessage);


// Send message to server to make a screenshot

screenshotBtn.addEventListener('click', sendMessage)

// Send message to server to start/stop a record

recordBtn.style.display = 'none';
recordBtn.addEventListener('click', sendMessage)




// Emojis layout

const emojis = ["🙂", "😐", "😀", "😂", "🤔", "👍", "🖕", "🤟", "🫀", "🐈", "🐈‍⬛", "🌸"];

for (let i = 0; i < emojis.length; i++) {
  const link = document.createElement("a");
  link.setAttribute("class", "emoji");
  link.setAttribute("onclick", "$('#chatInput').val($('#chatInput').val() + this.textContent)");
  link.textContent = emojis[i];
  let node = document.getElementById('emojis');
  node.appendChild(link);
}