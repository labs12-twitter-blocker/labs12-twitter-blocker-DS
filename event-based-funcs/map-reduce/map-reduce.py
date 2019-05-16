import base64
import time
from google.cloud import pubsub_v1
from google.cloud import firestore
import ast
import os


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
            data_list[x[0]].update({x[1]:x[2]})
            seen.add(x[0])
        else:
            data_list[x[0]].update({x[1]:x[2]})
    
    
    
    print(data_list)
    print(seen)
    post_to_db(data_list, seen)
    
    
    
    
    
    
    
    
    
    
    
    
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
    message.ack()
    global job_id
    message_num = job_id
    message_data = message.data.decode('utf-8')
    message_data = ast.literal_eval(message_data)
    message_id = int(message_data[0])
    print(message_id)
    if message_id == message_num:
        
        #print('Received message: {}'.format(message))
        interactions = message_data[1]
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
        
        
    
    
    
    
    
    
 