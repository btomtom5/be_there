$(function () {
  console.log('Requesting Capability Token...');
  $.getJSON('/voice_token')
    .done(function (data) {
      console.log('Got a token.');
      console.log('Token: ' + data.token);

      setUpVoiceComm(data);
    })
    .fail(function () {
      console.log('Could not get a token from server!');
    });
});


function setUpVoiceComm(data){
  // Setup Twilio.Device
  Twilio.Device.setup(data.token);

  Twilio.Device.ready(function (device) {
    console.log('Twilio.Device Ready!');
    document.getElementById('call-controls').style.display = 'block';
  });

  Twilio.Device.error(function (error) {
    console.log('Twilio.Device Error: ' + error.message);
  });

  Twilio.Device.connect(function (conn) {
    console.log('Successfully established call!');
    document.getElementById('button-call').style.display = 'none';
    document.getElementById('button-hangup').style.display = 'inline';
  });

  Twilio.Device.disconnect(function (conn) {
    console.log('Call ended.');
    document.getElementById('button-call').style.display = 'inline';
    document.getElementById('button-hangup').style.display = 'none';
  });

  Twilio.Device.incoming(function (conn) {
    console.log('Incoming connection from ' + conn.parameters.From);
    var archEnemyPhoneNumber = '+12099517118';

    if (conn.parameters.From === archEnemyPhoneNumber) {
      conn.reject();
      console.log('It\'s your nemesis. Rejected call.');
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
    console.log('Hanging up...');
    Twilio.Device.disconnectAll();
  };
}