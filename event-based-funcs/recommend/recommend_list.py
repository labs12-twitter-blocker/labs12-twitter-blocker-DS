import random
import base64
import ast
import json
import time

from google.cloud import pubsub_v1

from google.cloud import firestore

import pandas as pd
import numpy as np
import networkx as nx



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
    
    data = unpack_from_db(users_list)
    print(data)
    
    
    response = pagerank(data, users_list)
    
    
    return response
    
    
    
    
 

    
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
            
            num_to_search = len(search_users)
            job_data = []
            global job_id
            job_id = random.randint(100000,999999)
            job_data.append(search_users)
            job_data.append(TWITTER_ACCESS_TOKEN)
            job_data.append(TWITTER_ACCESS_TOKEN_SECRET)
            job_data.append(job_id)
            job_data.append(num_to_search)
            
            
            
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
        
        
        
        print('finished processing')
    
    
    
        global num_recieved
        num_recieved = num_recieved + 1
    else:
        print("recieved message id: ", message_id)
        print("expected message id: ", message_num)
    

def unpack_from_db(users):
    output = []
    
    #project_id = os.environ['GCP_PROJECT']
    db = firestore.Client()
    
    
    
    for user in users:
        get_user = db.collection(u'interactions').document(user).get()
        user_info = get_user.to_dict()
        print(user)
        print(user_info)
        if user_info is not None:
            for key, value in user_info.items():
                if key == 'timestamp':
                    print('hit a timestamp')
                else:
                    output.extend([(user, key) for interaction in range(value)])
                
    return output
        
    
def pagerank(data, users):
    # DF before Groupby (Turn response data into pandas df)
    t = time.time()
    df = pd.DataFrame(data, 
                      columns=['source_user', 'interaction_user'])

    # Create groupby counts
    df_group = (df.groupby(['source_user','interaction_user'])
                  .size().reset_index().rename(columns={0: "count"}))

    # Create "Normalized" interaction weights for each user's interactions. 
    a = df_group.groupby('source_user')['count'].transform('sum')
    df_group['weight'] = df_group['count'].div(a)
    print("normalized data via groupby")
    
    
    print('data formatting took: ', time.time()-t)
    print(df_group.head(20))

    # Create the directional graph object. 
    # (Uses weight or count derived summaries.)
    t = time.time()
    DG = nx.from_pandas_edgelist(df_group, "source_user", "interaction_user",
                                edge_attr=['weight', "count"], 
                                create_using=nx.DiGraph())
    found_nodes = nx.number_of_nodes(DG)
    print("converted df to graph with %s nodes", found_nodes)
    print('convert df to graph took: ', time.time()-t)

    # Pagerank it!
    t = time.time()
    pr = nx.pagerank_numpy(DG, alpha= 0.85, weight="weight") 
    dg_pr_df = pd.DataFrame([pr]).T.reset_index() 
    dg_pr_df = dg_pr_df.rename(index=str, columns={"index": "username", 0: "pagerank"})
    dg_pr_df = dg_pr_df.sort_values(by=['pagerank'], ascending=False)
    print("pageranked the values")
    print("pagerank took: ", time.time()-t)
    
    
    output = return_json(dg_pr_df, users, found_nodes)
    return output


def return_json(pageranked_df, search_target_users, qty_users_found):
    ranked_dict = pageranked_df[["username"]].head(50).username.tolist()
    #search_dict = {("search_user_%s" % i) : search_target_users[i] for i in range(0, len(search_target_users))}
    final_dict = {
                    
                  "ranked_results": ranked_dict
              
    }
    final_json = json.dumps(final_dict)
    return final_json # Returns JSON string. 
