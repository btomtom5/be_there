$(function () {
  log('Requesting Capability Token...');
  $.getJSON('/voice_token')
    .done(function (data) {
      log('Got a token.');
      console.log('Token: ' + data.token);

      setUpVoiceComm(data);

      setClientNameUI(data.identity);
    })
    .fail(function () {
      log('Could not get a token from server!');
    });

  // $.getJSON('/video_token')
  //   .done(function(data){
  //     log('Got a token.');
      
  //     setUpVideoComm(data);

  //   })

});

// Activity log
function log(message) {
  var logDiv = document.getElementById('log');
  logDiv.innerHTML += '<p>&gt;&nbsp;' + message + '</p>';
  logDiv.scrollTop = logDiv.scrollHeight;
}

// Set the client name in the UI
function setClientNameUI(clientName) {
  var div = document.getElementById('client-name');
  div.innerHTML = 'Your client name: <strong>' + clientName +
    '</strong>';
}

function setUpVoiceComm(data){
  // Setup Twilio.Device
  Twilio.Device.setup(data.token);

  Twilio.Device.ready(function (device) {
    log('Twilio.Device Ready!');
    document.getElementById('call-controls').style.display = 'block';
  });

  Twilio.Device.error(function (error) {
    log('Twilio.Device Error: ' + error.message);
  });

  Twilio.Device.connect(function (conn) {
    log('Successfully established call!');
    document.getElementById('button-call').style.display = 'none';
    document.getElementById('button-hangup').style.display = 'inline';
  });

  Twilio.Device.disconnect(function (conn) {
    log('Call ended.');
    document.getElementById('button-call').style.display = 'inline';
    document.getElementById('button-hangup').style.display = 'none';
  });

  Twilio.Device.incoming(function (conn) {
    log('Incoming connection from ' + conn.parameters.From);
    var archEnemyPhoneNumber = '+12099517118';

    if (conn.parameters.From === archEnemyPhoneNumber) {
      conn.reject();
      log('It\'s your nemesis. Rejected call.');
    } else {
      // accept the incoming connection and start two-way audio
      conn.accept();
    }
  });

    // Bind button to make call
  document.getElementById('button-call').onclick = function () {
    // get the phone number to connect the call to
    var params = {
      To: document.getElementById('phone-number').value
    };

    console.log('Calling ' + params.To + '...');
    Twilio.Device.connect(params);
  };

  // Bind button to hangup call
  document.getElementById('button-hangup').onclick = function () {
    log('Hanging up...');
    Twilio.Device.disconnectAll();
  };
}

function setUpVideoComm(data){
  Twilio.Video.connect(data.access_token, {name:'my-new-room'}).then(
    function(room) {
      console.log('Successfully joined a Room: ', room);
      room.on('participantConnected', 
        function(participant) {
          console.log('A remote Participant connected: ', participant);
        })
    }, function(error) {
        console.error('Unable to connect to Room: ' +  error.message);
      });
}