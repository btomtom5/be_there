#!/usr/bin/env python
import logging
import os
import re
from flask import Flask, jsonify, request, Response, send_file
from faker import Factory
from twilio.jwt.client import ClientCapabilityToken
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant, VideoGrant

logging.basicConfig(filename='logs/routing.log',level=logging.DEBUG)

app = Flask(__name__)
fake = Factory.create()
client_name = 'RealMonkey'
alphanumeric_only = re.compile('[\W_]+')
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")



@app.route('/remote_client')
def remote_client():
    return send_file('remote_client/parent_client.html')

@app.route('/home_client')
def home_client():
    return send_file('home_client/home_client.html')


@app.route('/voice_token', methods=['GET', 'POST'])
def voice_token():
    # get credentials for environment variables
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    voice_sid = os.environ['TWILIO_TWIML_APP_SID']

    # Generate a random user name
    identity = alphanumeric_only.sub('', fake.user_name())

    # Create a Capability Token
    capability = ClientCapabilityToken(account_sid, auth_token)
    capability.allow_client_outgoing(voice_sid)
    capability.allow_client_incoming(identity)
    token = capability.to_jwt()

    # Return token info as JSON
    return jsonify(
        identity=identity,
        token=token.decode('utf-8'))

@app.route('/video_token', methods=['GET', 'POST'])
def video_token():
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    video_sid = os.environ['TWILIO_VIDEO_API_SID']
    video_secret = os.environ['TWILIO_VIDEO_API_SECRET']

    # Generate a random user name
    identity = alphanumeric_only.sub('', fake.user_name())

    #Create an Access Token
    access = AccessToken(account_sid, video_sid, video_secret)
    access.identity = identity
    video_grant = VideoGrant()
    access.add_grant(video_grant)
    access_token = access.to_jwt() 

    return jsonify(
            identity=identity,
            token=access_token.decode('utf-8'))



@app.route("/voice", methods=['POST'])
def voice():
    resp = VoiceResponse()
    if "To" in request.form and request.form["To"] != '':
        dial = Dial(caller_id=os.environ['TWILIO_CALLER_ID'])
        # wrap the phone number or client name in the appropriate TwiML verb
        # by checking if the number given has only digits and format symbols
        if phone_pattern.match(request.form["To"]):
            dial.number(request.form["To"])
        else:
            dial.client(request.form["To"])
        resp.append(dial)
    else:
        resp.say("Thanks for calling!")

    return Response(str(resp), mimetype='text/xml')


@app.route('/receive_call', methods=['GET'])
def receive_call():
    return send_file('remote_client/incoming_call.xml')

if __name__ == '__main__':
    app.run(debug=True)
