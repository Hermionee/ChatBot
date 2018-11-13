import json
import boto3
from botocore.vendored import requests
from botocore.config import Config
import time
def lambda_handler(event, context):
    # TODO implement
    sqs = boto3.resource('sqs')
    queue_url = "https://sqs.us-east-1.amazonaws.com/267836282592/demand.fifo"
    squeue = sqs.Queue(queue_url)
    config = Config(
        connect_timeout=600, read_timeout=600,
        retries={'max_attempts': 10})
    dynamo = boto3.client('dynamodb', config=config)
    queue = sqs.get_queue_by_name(QueueName='demand.fifo')

    response = queue.receive_messages(MessageAttributeNames=['All'],
        MaxNumberOfMessages=1,
        VisibilityTimeout=30,
        WaitTimeSeconds=20)
        # ReceiveRequestAttemptId='string'
    for m in response:
        messages = m.message_attributes
        receipt_handle = m.receipt_handle
        apikey="0fiGprRIaqe9HrKQjeZ4nMToRyTawiNWvGzhXstOhJs_MQnyPFDxZ8NsgpHaTV4ziItIwNxii66EKugSvHSjMD38HffYIxrXhZwUzKJifXXsG7tL8VvPxe-snVrnW3Yx"
        clientId="kqmcMwsr6PN0rszkuWZSUQ"
        dt = messages["dining_date"]['StringValue']+" "+messages["dining_time"]['StringValue']+":00"
        timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
        dt_new = time.strftime("%Y%m%d %H%M",timeArray)
        dt_new= int(dt_new[:8] + dt_new[9:])
        params={
            "term":"restaurants",
            "location":messages["location"]['StringValue'],
            # "open_at":dt_new,
            "categories": messages["cuisine"]['StringValue'],
            "sort_by": 'rating'
        }
        
        headers={"Authorization": "Bearer 0fiGprRIaqe9HrKQjeZ4nMToRyTawiNWvGzhXstOhJs_MQnyPFDxZ8NsgpHaTV4ziItIwNxii66EKugSvHSjMD38HffYIxrXhZwUzKJifXXsG7tL8VvPxe-snVrnW3Yx"}
        myResponse = requests.get("https://api.yelp.com/v3/businesses/search", headers=headers, params=params)
        
        # Delete received message from queue
        squeue.delete_messages(Entries=[
        {
            'Id': m.message_id,
            'ReceiptHandle': m.receipt_handle
        }])
        print "Received and deleted message"
        r = myResponse.json()
        print len(r['businesses'])
        # dynamo.batch_write_item(RequestItems={
        # 'Recommendation': [
        #     {
        #         'PutRequest': {
        #             'Item':{
        #                     'restaurantId':
        #                     {
        #                     'S': str(i)
        #                     },
        #                     'name':
        #                     {
        #                         'S': r['businesses'][i]['name']
        #                      },
        #                     'rating':
        #                     {
        #                     'N': str(r['businesses'][i]['rating'])
        #                     },
        #                     'city':{
                #                 'S': r['businesses'][i]['location']['city']
                #             },
                #             'address':{
                #                 "S": r['businesses'][i]['location']['address1']
                #             },
                #             'phone':{
                #                 'S': messages['Phone']['StringValue']
                #             },
                #             'closed':{
                #                   'BOOL': r['businesses'][i]['is_closed']
                #              }
                #             }
                #             }
                #             }
                #         ]
                #     },
                #     ReturnConsumedCapacity='TOTAL',
                #     ReturnItemCollectionMetrics='SIZE'
                # )
        
        for i in range(len(r['businesses'])):
            print i
            Item = {'restaurantId':{
                'S': str(i)
            },
                'name':
                        {
                            'S': r['businesses'][i]['name']
                        },
                    'rating':
                        {
                        'N': str(r['businesses'][i]['rating'])
                    },
                    'city':{
                            'S': r['businesses'][i]['location']['city']
                    },
                    'address':{
                        "S": r['businesses'][i]['location']['address1'] if r['businesses'][i]['location']['address1']!="" else "null"
                    },
                    'phone':{
                            'S': messages['Phone']['StringValue']
                    },
                    'closed':{
                            'BOOL': r['businesses'][i]['is_closed']
                    }
            }
            dynamo.put_item(TableName = 'Recommendation', Item = Item, ReturnValues = 'NONE')
        print "dynamo done"
        sns = boto3.client('sns')
        best_restaurant = dynamo.get_item(TableName = 'Recommendation', Key = {'restaurantId':{'S': str(0)}, 'phone':{'S':messages['Phone']['StringValue']}}, AttributesToGet=['name','address','city','rating'])
        print best_restaurant['Item']['city']
        print best_restaurant['Item']['address']
        print best_restaurant['Item']['name']
        print best_restaurant['Item']['rating']
        response = sns.publish(
        PhoneNumber = messages['Phone']['StringValue'],
        Message="In "+best_restaurant['Item']['city']['S']+" "+best_restaurant['Item']['address']['S']+" "+best_restaurant['Item']['name']['S']+" rating:"+str(best_restaurant['Item']['rating']['N']),
        # MessageStructure='json',
        MessageAttributes={
            'name': {
                'DataType': 'String',
                'StringValue':best_restaurant['Item']['name']['S']
            },
            'address': {
                'DataType': 'String',
                'StringValue':best_restaurant['Item']['address']['S']
            },
            'city': {
                'DataType': 'String',
                'StringValue':best_restaurant['Item']['city']['S']
            },
            'rating': {
                'DataType': 'Number',
                'StringValue':str(best_restaurant['Item']['rating']['N'])
            }
        }
        )
        print response
        print "sns sent"

