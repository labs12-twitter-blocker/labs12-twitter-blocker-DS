import base64
import time
from google.cloud import pubsub_v1
from google.cloud import firestore
import ast
import os
import datetime
import json



def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
         
    """
    broke = False
    start = time.time()
    print(start)
    
    global job_id
    job_id = base64.b64decode(event['data']).decode('utf-8')
    job_id = int(job_id)
    
    
    global data
    data = []
    global num_recieved
    num_recieved = 0
    
    
    global users_list
    users_list = []
    
    
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path('bert-optimization-testing', 'interaction_listener')
    
    
   
    subscriber.subscribe(subscription_path, callback=process_data)
    print('Listening for messages on {}'.format(subscription_path))

    while num_recieved < 5:
        time.sleep(1)
        now = time.time()
        print("has been running for: ", now)
        if now - start > 20:
            broke = True
            print("OH SH- it broke - SHOCKER")
            return
        
    if broke == True:
        return
    
    
    
    print('loop finished')
    
    data = map_reduce1(data)
    print(data)
    
    seen = set()
    data_list = {}
    index = -1
    for x in data:
        if x[0] not in seen:
            index += 1
            data_list[x[0]] = {}
            data_list[x[0]].update({'timestamp': datetime.datetime.utcnow()})
            data_list[x[0]].update({x[1]:x[2]})
            seen.add(x[0])
        else:
            data_list[x[0]].update({x[1]:x[2]})
    
    
    
    print(data_list)
    print(seen)
    post_to_db(data_list, seen)
    users_list = list(set(users_list))
    print('Users in Job:', users_list)
    publish(job_id, users_list)
    
    
    
    
    
    
    
    
    
    
    
    
    #pubsub_message = base64.b64decode(event['data']).decode('utf-8')

    
def map_reduce1(data):
    seen = set()
    data_list = []
    index = -1
    for x in data:
        if x not in seen:
            index += 1
            data_list.append(list(x))
            data_list[index].append(1)
            seen.add(x)
        else:
            data_list[index][2] += 1
    return data_list
    
    
    
    
def process_data(message):
    global job_id
    message_num = job_id
    message_data = message.data.decode('utf-8')
    message_data = ast.literal_eval(message_data)
    message_id = int(message_data[0])
    print(message_id)
    if message_id == message_num:
        message.ack()
        
        #print('Received message: {}'.format(message))
        users_in_job = message_data[1]
        users_list.extend(users_in_job)
        
        
        
        
        interactions = message_data[2]
        print(interactions)
        global data
        data.extend([tuple(x) for x in interactions])
        print(data[0])
        test = data[0]
        print(type(test))
        print('finished processing')
    
    
    
        global num_recieved
        num_recieved = num_recieved + 1
    else:
        print("recieved message id: ", message_id)
        print("expected message id: ", message_num)
    
    
    
    
    
def post_to_db(data, names):
    project_id = os.environ['GCP_PROJECT']
    db = firestore.Client()
    batch = db.batch()
    for name in names:
        entry = data[name]
        batch.set(db.collection(u'interactions').document(name), entry)
    batch.commit()
    
    
def publish(job_id, users_list):
    """Publishes a message to a Pub/Sub topic."""
    client = pubsub_v1.PublisherClient()
    
    
    # `projects/{project_id}/topics/{topic_name}`
    topic_path = client.topic_path('bert-optimization-testing', 'db_listener')
    
    
    output = []
    output.append(job_id)
    output.append(users_list)
    
    #encode to send message to workers
    data = json.dumps(output, ensure_ascii=False).encode('utf8')
    
    
    
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
    
    
    
    
    
    
 
        
    
    
    
    
    
    
 