import os
from gnewsclient import gnewsclient
from geopy.geocoders import Nominatim
import requests,json


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client-secret.json"

import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "helpbot-xddjoe"


news_client = gnewsclient.NewsClient()
geolocator = Nominatim(user_agent="HelpBot")



def get_news(parameters):
	print(parameters)
	news_client.topic = parameters.get('news_type')
	news_client.language = parameters.get('language')
	news_client.location = parameters.get('geo-country')
	return news_client.get_news()


def get_temp(parameters):
	print(parameters)


	api_key = "b94ee259ae28311262635714dfacdfe1"
   
	base_url = "http://api.openweathermap.org/data/2.5/weather?"
	city_name = parameters.get('geo-city')

	complete_url = base_url + "appid=" + api_key + "&q=" + city_name 

	r = requests.get(complete_url) 
	  
	if r.json()['cod'] != '404':

		city = r.json()['name']
		temp = round(r.json()['main']['temp']-273,2) 
		hum = r.json()['main']['humidity']
		desc = r.json()['weather'][0]['description']

		show_details = 'Current Weather of  *{}* is: \n*Temperature* : *{}°C* \n*Humidity* : *{}%* \n*Description* : *{}*'.format(city, temp, hum, desc)
		return (show_details)

	else:
		return "City not found!"

def get_restaurant(parameters):
	print(parameters)
	city = parameters.get('geo-city')
	
	
	if city == '':
		area = parameters.get('geo-location')['subadmin-area']
		location = geolocator.geocode(area, timeout=None)
		lat = location.latitude
		lon = location.longitude


	else:
		location = geolocator.geocode(city,timeout = None)
		lat = location.latitude
		lon = location.longitude

	api_key = 'c7b754018dbf2b1f1ffd87c26934f784'
	headers = {'user-key': api_key}
	
	r = requests.get('https://developers.zomato.com/api/v2.1/geocode?lat='+str(lat)+'&lon='+str(lon), headers=headers)

	show_details = 'Top Restaurants in *{}* near *{}* \n'.format(r.json()['location']['city_name'], r.json()['location']['title'])
	for i in range(5):
		name  = r.json()['nearby_restaurants'][i]['restaurant']['name']
		url = r.json()['nearby_restaurants'][i]['restaurant']['url']
		addr = r.json()['nearby_restaurants'][i]['restaurant']['location']['address']
		rating = r.json()['nearby_restaurants'][i]['restaurant']['user_rating']['aggregate_rating']

		show_details += "\n*Name :* *{}*\n*Address* : *{}*\n*Rating :* *{}*★\n {}\n".format(name,addr,rating,url)

	return show_details


def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result


def fetch_reply(msg, session_id):
	response = detect_intent_from_text(msg,session_id)

	if response.intent.display_name == 'get_news':		
		# return "news will be displayed! *{}*".format(dict(response.parameters))
		news = get_news(dict(response.parameters))
		news_str = 'Here are your *{}* news!'.format(news_client.topic)
		for row in news:
			news_str += "\n\n{}\n\n{}\n\n".format(row['title'],row['link'])
		print(news_str)
		return news_str[:1000]

	if response.intent.display_name == 'get_temp':
		temp = get_temp(dict(response.parameters))
		return '{}'.format(temp)

	if response.intent.display_name == 'get_restaurant':
		rest_details = get_restaurant(dict(response.parameters))
		return rest_details
	else:
		return response.fulfillment_text