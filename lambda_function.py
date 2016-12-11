import urllib2
import json

def lambda_handler(event, context):
    
    if(event['session']['application']['applicationId'] != 
        "amzn1.ask.skill.c41c9e71-ae85-4da2-b8dd-d96d463db1d2"):
        raise ValueError("Invalid Application ID")
    if event['session']['new']:
    	on_session_started({"requestId":event["request"]["requestId"]}, event['session'])

    if event['request']['type'] == "LaunchRequest":
    	return on_launch(event["request"], event["session"])
    elif event['request']['type'] == "IntentRequest":
    	return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
	print "Starting a new session."

def on_launch(launch_request, session):
	return get_welcome_response()

def on_intent(intent_request, session):
	intent = intent_request['intent']
	intent_name = intent_request['intent']['name']

	if intent_name == "ReadFrontPage":
		return read_front_page()
 	elif intent_name == "ReadCSCareerQuestions":
 		return read_cs_career_questions()
	elif intent_name == "Read":
 		return read_page(intent)
 	elif intent_name == "ReadComments":
 		return read_comments(intent, session)
	elif intent_name == "AMAZON.HelpIntent":
		return get_welcome_response()
	elif intent_name =="AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		return handle_session_end_request()
	else:
		raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
	print "Session ended."

def handle_session_end_request():
	card_title = "Reddit - Thanks Redditor!"
	speech_output = "Thank you for using the Reddit Reader Skill!"
	end_session = True

	return build_response({}, build_speechlet_response(card_title, speech_output, None, end_session))

def get_welcome_response():
	session_attributes = {}
	card_title = "Reddit"
	speech_output = "Welcome to the Alexa Reddit reader skill. I can read from " \
					"the front page of Reddit, CS Career Questions, or a number of " \
					"other pages."
	reprompt_text = "I can read from many Reddit pages, just ask."
	end_session = False;
	return build_response(session_attributes, build_speechlet_response(card_title,
		speech_output, reprompt_text, end_session))

def read_front_page():
	card_title = "Reddit Front Page"
	end_session = False;
	reprompt_text = ""

	page_entries = get_page_entries("http://www.reddit.com/.json")
	session_attributes = {"url": "http://www.reddit.com/.json"}
	speech_output = "First Thread " + page_entries[0] + "Second Thread " + page_entries[1] + \
					"Third Thread" + page_entries[2] + "Fourth Thread" + page_entries[3] + \
					"Fifth Thread" + page_entries[4]
    
	return build_response(session_attributes, build_speechlet_response(
    	card_title, speech_output, reprompt_text, end_session))

def read_cs_career_questions():
	card_title = "CS Career Questions"
	end_session = False;
	reprompt_text = ""

	page_entries = get_page_entries("http://www.reddit.com/r/cscareerquestions/.json")
	session_attributes = {"url": "http://www.reddit.com/r/cscareerquestions/.json"}
	speech_output = "First Thread " + page_entries[0] + "Second Thread " + page_entries[1] + \
					"Third Thread" + page_entries[2] + "Fourth Thread" + page_entries[3] + \
					"Fifth Thread" + page_entries[4]
    
	return build_response(session_attributes, build_speechlet_response(
    	card_title, speech_output, reprompt_text, end_session))

def read_page(intent):
	session_attributes = {}
	card_title = "SubReddit"
	speech_output = "I'm not sure which reddit page you wanted to read, please try again."
	reprompt_text = "I don't know which reddit page you are looking for, try asking about" \
					"space for example."
	end_session = False

	if "Read" in intent["slots"]:
		page_name = intent["slots"]["Read"]["value"]
		page_url = "http://www.reddit.com/r/" + page_name + "/.json"
		card_title = page_name + " SubReddit"
		page_entries = get_page_entries(page_url)
		session_attributes = {"url": "http://www.reddit.com/r/" + page_name + "/.json"}
		speech_output = "First Thread " + page_entries[0] + "Second Thread " + page_entries[1] + \
					"Third Thread" + page_entries[2] + "Fourth Thread" + page_entries[3] + \
					"Fifth Thread" + page_entries[4]
		reprompt_text = ""

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, end_session))

def read_comments(intent):
	session_attributes = {}
	card_title = "Comments"
	speech_output = "I didn't catch which thread you wanted me to read"
	reprompt_text = "Try saying read comments 1 or read comments 3"
	end_session = False
	if 'url' in session['attributes']:
		session_url = session['attributes']['url']
		session_attributes = {"url": session_url}

	if "Comment" in intent["slots"]:
		thread_idx = intent["slots"]["Comment"]["value"] - 1

		api = urllib2.build_opener()
		api.addheaders = [('User-Agent', 'Alexa Reddit Reader/1.0')]
		data = api.open(session_url);
		response = data.read()

		url_list = []
		idx = response.find("\"permalink\"") 
		counter = 0
		while(idx != -1 and counter < 7):
			quote = response.find("\"", idx + 17)
			urlx = response[idx + 15: quote]
			url_list.append("www.reddit.com/r/" + urlx)
			response = response[idx + 17:]
			idx = response.find("\"permalink\"") 
			counter += 1

		url = url_list[thread_idx] + ".json"
		card_title = "Thread " + str(thread_idx)
		comments = get_comments(url)
		speech_output = "First Comment - " + comments[0] + " - Second Comment  - " + comments[1] + \
					" - Third Comment - " + comments[2] + " - Fourth Comment - " + comments[3] + \
					" - Fifth Comment - " + comments[4]
		reprompt_text = ""

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, end_session))


def get_comments(url):
	api = urllib2.build_opener()
	api.addheaders = [('User-Agent', 'Alexa Reddit Reader/1.0')]
	data = api.open(url)

	response = data.read()
	comments = []
	comment_entry = response.find("\"body\"")
	counter = 0

	while(comment_entry != -1 and counter < 7):
		quote = response.find("\"", comment_entry + 9)
		comment = response[comment_entry + 9: quote]
		reply = response.find("\"replies\"")
		if response[reply + 11:reply + 13] == "\"\"":
			comments.append(comment)
			counter += 1

		response = response[comment_entry + 9:]
		comment_entry = response.find("\"body\"") 

	return comments
    
def get_page_entries(url):
	api = urllib2.build_opener()
	api.addheaders = [('User-Agent', 'Alexa Reddit Reader/1.0')]
	data = api.open(url);

	response = data.read()
	title_list = []
	title_entry = response.find("\"title\"");
	counter = 0
	while(title_entry != -1 and counter < 7):
		quote = response.find("\"", title_entry + 10)
		title = response[title_entry + 10: quote]
		title_list.append(title)
		response = response[title_entry + 10]
		title_entry = response.find("\"title\"")
		counter += 1

	return title_list


def build_speechlet_response(title, speech, reprompt, end_session):
	return {
		"outputSpeech": {
			"type": "PlainText",
			"text": speech
		},
		"card": {
			"type": "Simple",
			"title": title,
			"content": speech
		},
		"reprompt": {
			"outputSpeech": {
				"type": "PlainText",
				"text": reprompt
			}
		},
		"shouldEndSession": end_session
	}

def build_response(session_attributes, speechlet):
	return {
		"version": "1.0",
		"session_attributes": session_attributes,
		"response": speechlet
	}
