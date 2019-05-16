import base64
import time
from google.cloud import pubsub_v1
import ast



def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
         
    """
    global data
    data = []
    global num_recieved
    num_recieved = 0
    
    
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path('bert-optimization-testing', 'interaction_listener')
    
    
   
    subscriber.subscribe(subscription_path, callback=process_data)
    print('Listening for messages on {}'.format(subscription_path))

    while num_recieved < 2:
        time.sleep(1)
    
    print('loop finished')
    
    data = map_reduce1(data)
    print(data)
    
    seen = set()
    data_list = {}
    index = -1
    for x in data:
        if x[0] not in seen:
            index += 1
            data_list[x[0]] = []
            data_list[x[0]].append([x[1],x[2]])
            seen.add(x[0])
        else:
            data_list[x[0]].append([x[1],x[2]])
    
    
    
    print(data_list)
    print(seen)
    
    
    
    
    
    
    
    
    
    
    
    
    
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
    print('Received message: {}'.format(message.data))
    message.ack()
    interactions = message.data.decode('utf-8')
    print(interactions)
    interactions = ast.literal_eval(interactions)
    print(interactions)
    global data
    data.extend([tuple(x) for x in interactions])
    print(data[0])
    test = data[0]
    print(type(test))
    print('finished processing')
    
    
    
    global num_recieved
    num_recieved = num_recieved + 1
    
    
    
    
    
 def post_to_firestore(data, count, user):
    
    
    #To see what this does
    #https://colab.research.google.com/drive/1Y5xvcvOoUSSXxQmqO1wW_jqyruwq03wG
    
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
            
            
            
    
    
                                   
                                   
                                   
                                   
                                   
    
    
    
    project_id = os.environ['GCP_PROJECT']
    
    
    
    
    
    
    
    db = firestore.Client()
    doc_ref = db.collection(u'interactions').document(user)
    doc_ref.set({
        u'count': count,
    })
    
    
    for i in range(len(data_list)):
        title = u'interaction: ' + str(i)
        doc_ref.set({
            title: data_list[i]
        })