import os

from flask import Flask
from flask import Response
from flask import request
from flask import render_template
from twilio import twiml
from twilio.rest import TwilioRestClient

# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Create a Flask web app
app = Flask(__name__)

# Render the home page
@app.route('/')
def index():
    return render_template('index.html')

# Handle a POST request to send a text message. This is called via ajax
# on our web page
@app.route('/message', methods=['POST'])
def message():
    # Send a text message to the number provided
    message = client.sms.messages.create(to=request.form['to'],
                                         from_=TWILIO_NUMBER,
                                         body='Good luck on your Twilio quest!')

    # Return a message indicating the text message is enroute
    return 'Message on the way!'

# Handle a POST request to make an outbound call. This is called via ajax
# on our web page
@app.route('/call', methods=['POST'])
def call():
    # Make an outbound call to the provided number from your Twilio number
    call = client.calls.create(to=request.form['to'], from_=TWILIO_NUMBER, 
                               url='http://twimlets.com/message?Message%5B0%5D=http://demo.kevinwhinnery.com/audio/zelda.mp3')

    # Return a message indicating the call is coming
    return 'Call inbound!'

# Generate TwiML instructions for an outbound call
@app.route('/hello')
def hello():
    response = twiml.Response()
    response.say('Hello there! You have successfully configured a web hook.')
    response.say('Good luck on your Twilio quest!', voice='woman')
    return Response(str(response), mimetype='text/xml')

@app.route('/respondtotext', methods=['POST'])
def respondtotext():
    # Respond to a text sent to the Twilio phone number
    response = twiml.Response()
    response.sms("Hello. Let's play a game. Answer these riddles correctly to win.....First question: What gets wetter the more it dries?")
    response.redirect('/checkriddleanswer')
    return Response(str(response), mimetype='text/xml')

    # text_content =request.values.get("Body", None)
    # if text_content == "A towel":
    #     response.sms("Congratulations! You win!")
    # return Response(str(response), mimetype='text/xml')

    ###BEFORE RIDDLE
    #return Response(str(response), mimetime='text/xml')
    # response = twiml.Response()
    # response.sms("Hello! I am responding to your text via text! :D")
    # return Response(str(response), mimetype='text/xml')

    # # Return a message indicating the message is on its way
    # return 'Sending response to a text!'
@app.route('/checkriddleanswer', methods=['GET', 'POST'])
def check_riddle_answer():
    text_content =request.values.get("Body", None)
    if text_content == "A towel":
        response.sms("Congratulations! You win!")
    else:
        response.sms("Nope, you lose.")
    return Response(str(response), mimetype='text/xml')

@app.route('/respondtocall', methods=['GET'])
def respondtocall():
    # Respond to a call to the Twilio phone number
    response = twiml.Response()
    gather = response.gather(action= '/respondtoinput')
    gather.say("Hello. If you would like to leave a message, press 1, then pound. If you would like to play back the last recorded message, press 2, then pound.")
    return Response(str(response), mimetype='text/xml')

@app.route('/respondtoinput', methods=['GET', 'POST'])
def respondtoinput():
    # Respond to the user input from /responsetocall
    response = twiml.Response()
    recording_url = request.values.get("RecordingUrl", None)

    if request.values["Digits"] == "1":
        response.say("Please record your message after the tone.")
        response.record(timeout = "5", action='/handle_recording')
    elif request.values["Digits"] == "2":
        response.say("Here is the last recorded message.")
        response.play(recording_url, loop=1)
        response.play("Goodbye.")
    elif request.values["Digits"]== "0":
        response.say("Stay on the line for an operator.")
        response.dial("+16177941160")
    else:
        respond.say("Please try again.")
        response.redirect('/respondtocall')
    return Response(str(response), mimetype='text/xml')

@app.route('/handle_recording', methods=['GET', 'POST'])
def handle_recording():

    recording_url=request.values.get("RecordingUrl", None)
    response = twiml.Response()
    response.say("Here is the message you recorded.")
    response.play(recording_url, loop=1)
    response.say("Goodbye.")
    return Response(str(response), mimetype='text/xml')



if __name__ == '__main__':
    # Note that in production, you would want to disable debugging
    app.run(debug=True)