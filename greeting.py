
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
import json
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_dining_config(location, cuisine, time, date, number, phone):
    cuisines = ['indian', 'chinese', 'bavarian', 'british', 'french', 'japanese','korean','american']
    if cuisine is not None and cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'cuisine',
                                       'I dont\'t know about good {} restaurants, would you like a different type of food?  '
                                       'Our most popular restaurants are Chinese restaurant'.format(cuisine))
    # # get a dictionary of cities: 'c'
    # gc = geonamescache.GeonamesCache()
    # c = gc.get_cities()
    # 
    # # extract the US city names and coordinates
    # US_cities = [c[key]['name'] for key in list(c.keys())
    # #              if c[key]['countrycode'] == 'US']
    city = ['new york', 'phelidelphia', 'boston', 'los angelos']
    if location is not None and location.lower() not in city:
        return build_validation_result(False,
                                      'location',
                                      'Sorry, we haven\'t extended our service to {}. We are working on that!'.format(location))
    # get a dictionary of cities: 'c'
    # gc = geonamescache.GeonamesCache()
    # c = gc.get_cities()
    # 
    # # extract the US city names and coordinates
    # US_cities = [c[key]['name'] for key in list(c.keys())
    #              if c[key]['countrycode'] == 'US']
    if phone is not None:
        if len(phone[2:]) != 10:
            return build_validation_result(False, 'Phone', 'Sorry, this is not valid phone number. Could you check again?')

    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'diningTime', 'I did not understand that, what date would you like to eat?')

    if time is not None:
        if len(time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'diningTime', 'Not valid time format! Please try again!')

        hour, minute = time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'diningTime', 'Not valid time format! Please try again!')

        if hour < 10 or hour > 22:
            # Outside of business hours
            return build_validation_result(False, 'diningTime', 'Restaurant hours are from 10 a m. to 10 p m. Can you specify a time during this range?')

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """

def say_hi(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Hi there! How can I help you?'})

def say_bye(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Bye, have a good day :p'})
                  
def dining(intent_request):
    location = get_slots(intent_request)["location"]
    cuisine = get_slots(intent_request)["cuisine"]
    dining_time = get_slots(intent_request)["diningTime"]
    dining_date = get_slots(intent_request)["diningDate"]
    number = get_slots(intent_request)["NumberPeople"]
    phone = get_slots(intent_request)["Phone"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)

        validation_result = validate_dining_config(location, cuisine, dining_time, dining_date, number, phone)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        if cuisine is not None:
            output_session_attributes['Price'] = len(cuisine) * 5  # Elegant pricing model

        return delegate(output_session_attributes, get_slots(intent_request))

    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='demand.fifo')
    response = queue.send_message(MessageBody = "demands from user" + phone, MessageGroupId = "12345",
    MessageAttributes={
              'Phone':{
                  'DataType':'String',
                  'StringValue':phone
              },
              'location':{
                  'DataType':'String',
                  'StringValue':location
              },
              'cuisine':{
                  'DataType':'String',
                  'StringValue':cuisine
              },
              'dining_time':{
                  'DataType':'String',
                  'StringValue':dining_time
              },
              'dining_date':{
                  'DataType':'String',
                  'StringValue':dining_date
              },
              'number':{
                  'DataType':'String',
                  'StringValue':number
              }
        })
    
    response = {
        # 'sessionAttributes': event['sessionAttributes'],
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message':{
                 "contentType": "PlainText",
                 "content": "Your reservations have been booked. Thank you. "
            }
        }
    }

    return response

""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return say_hi(intent_request)
    elif intent_name == 'ThankyouIntent':
        return say_bye(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return dining(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
