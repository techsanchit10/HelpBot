from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils import fetch_reply
from pymongo import MongoClient
import datetime

import json

db_client = MongoClient("mongodb+srv://admin:admin@cluster0-mvoqk.mongodb.net/test?retryWrites=true&w=majority")

db = db_client.get_database('helpbot_db')
records = db.helpbot_queries

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello, World!"

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    print(json.dumps(request.form,indent = 2))
    msg = request.form.get('Body')
    sender = request.form.get('From')
    reply = fetch_reply(msg,sender)

    # Store in DB
    new_record = { 'message_body': msg, 'sender_id' : sender, 'bot_reply': reply, 'sent_at' : str(datetime.datetime.now()) }
    records.insert_one(new_record)
    # # Create reply
    # # resp.message("You said: {}".format(msg)).media("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png")

    resp = MessagingResponse()
    if msg == 'help' or msg == 'Help' or msg =='HELP':
        resp.message("Hello, I am a *_HelpBot_*. How may I help you? \n\nYou can search for news by providing us the *news type*! \nEg: *show me sports news* \n\nYou can also search for *restaurants/cafes* in any area \nEg: *show me restaurants in gurgaon* \n\nYou can check the *temperature* of any paticular location \nEg: *what is the temperature of amritsar*")
    else:
        resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)