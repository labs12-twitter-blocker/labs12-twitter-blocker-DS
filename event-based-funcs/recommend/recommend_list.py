import random
import base64
import ast
import json
import time

from google.cloud import pubsub_v1

from google.cloud import firestore





def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
        
    """
    global job_id
    
    global users_list
    users_list = []
    
    
    job_data = process_request(request)
    
    publish(job_data)
    
    
    timed_out = listen_for_db()
    print(timed_out)
    
    print(users_list)
    
    
    test_str = ' '.join(users_list)
    
    return test_str
    
    
    
    
 

    
def process_request(request):
    """ Responds to a GET request with "Hello world!". Forbids a PUT request.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
         Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    from flask import abort

    content_type = request.headers['content-type']
    request_json = request.get_json(silent=True)
    request_args = request.args

    if content_type == 'application/json': 
        request_json = request.get_json(silent=True)
        # REFORMAT AS A FOR LOOP LATER
        
        
        
        # search_users check/set/error
        if request_json and 'search_users' in request_json:
            search_users = request_json['search_users']
        else:
            raise ValueError("JSON is invalid, or missing a 'search_users'")
            
        
        
        # TWITTER_ACCESS_TOKEN check/set/error
        if request_json and 'TWITTER_ACCESS_TOKEN' in request_json:
            TWITTER_ACCESS_TOKEN = request_json['TWITTER_ACCESS_TOKEN']
        else:
            raise ValueError("Missing a 'TWITTER_ACCESS_TOKEN'")
        
        
        
        
        # TWITTER_ACCESS_TOKEN_SECRET check/set/error
        if request_json and 'TWITTER_ACCESS_TOKEN_SECRET' in request_json:
            TWITTER_ACCESS_TOKEN_SECRET = request_json['TWITTER_ACCESS_TOKEN_SECRET']
        else:
            raise ValueError("Missing a 'TWITTER_ACCESS_TOKEN_SECRET'")
        
        
        
        # Call the function for the POST request. 
        if request.method == 'POST':
            
            
            job_data = []
            global job_id
            job_id = random.randint(100000,999999)
            job_data.extend(search_users)
            job_data.append(TWITTER_ACCESS_TOKEN)
            job_data.append(TWITTER_ACCESS_TOKEN_SECRET)
            job_data.append(job_id)
            
            
            
            return job_data
    else:
        return abort(405)
    
    
    
    
    
    
    
    
def publish(job_details):
    """Publishes a message to a Pub/Sub topic."""
    client = pubsub_v1.PublisherClient()
    
    
    # `projects/{project_id}/topics/{topic_name}`
    topic_path = client.topic_path('bert-optimization-testing', 'tweet_gather')
    
    #encode to send message to workers
    data = json.dumps(job_details, ensure_ascii=False).encode('utf8')
    
    
    
    # When you publish a message, the client returns a future.
    api_future = client.publish(topic_path, data=data)
    api_future.add_done_callback(get_callback(api_future, data))

    # Keep the main thread from exiting until background message
    # is processed.
    while api_future.running():
        time.sleep(0.1)
        
        
        
def get_callback(api_future, data):
    """Wrap message data in the context of the callback function."""

    def callback(api_future):
        try:
            print("Published message {} now has message ID {}".format(
                data, api_future.result()))
        except Exception:
            print("A problem occurred when publishing {}: {}\n".format(
                data, api_future.exception()))
            raise
    return callback



def listen_for_db():
    
    global num_recieved
    num_recieved = 0
    
    
    start = time.time()
    
    timed_out = False
    
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path('bert-optimization-testing', 'listen_for_job')
    
    
   
    subscriber.subscribe(subscription_path, callback=process_data)
    print('Listening for messages on {}'.format(subscription_path))
    
    while num_recieved < 1:
        time.sleep(1)
        now = time.time()
        print("has been running for: ", now)
        if now - start > 30:
            timed_out = True
            print("timed out!")
            return
        
    return timed_out
    
    
    
    
    
    
def process_data(message):
    message.ack()
    global job_id
    message_num = job_id
    message_data = message.data.decode('utf-8')
    message_data = ast.literal_eval(message_data)
    message_id = int(message_data[0])
    print(message_id)
    if message_id == message_num:
        
        #print('Received message: {}'.format(message))
        users_in_job = message_data[1]
        users_list.extend(users_in_job)
        
        
        
        print('finished processing')
    
    
    
        global num_recieved
        num_recieved = num_recieved + 1
    else:
        print("recieved message id: ", message_id)
        print("expected message id: ", message_num)
    

    
    
