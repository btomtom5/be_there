#!/usr/bin/env python
import logging
import os
import re
from flask import Flask, jsonify, request, Response, render_template
from faker import Factory
from twilio.jwt.client import ClientCapabilityToken
from twilio.twiml.voice_response import VoiceResponse, Dial

logging.basicConfig(filename='routing.log',level=logging.DEBUG)

app = Flask(__name__)
fake = Factory.create()
client_name = 'Real-Monkey'
alphanumeric_only = re.compile('[\W_]+')
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")



@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/token', methods=['GET', 'POST'])
def token():
    # get credentials for environment variables
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    application_sid = os.environ['TWILIO_TWIML_APP_SID']

    # Generate a random user name
    identity = alphanumeric_only.sub('', client_name)

    # Create a Capability Token
    capability = ClientCapabilityToken(account_sid, auth_token)
    capability.allow_client_outgoing(application_sid)
    capability.allow_client_incoming(identity)
    token = capability.to_jwt()

    # Return token info as JSON
    return jsonify(identity=identity, token=token.decode('utf-8'))


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

    return app.send_static_file('incoming_call.xml')

if __name__ == '__main__':
    app.run(debug=True)
