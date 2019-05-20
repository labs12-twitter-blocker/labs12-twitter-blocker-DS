import base64
import ast



import json
import tweepy
import re
from collections import Counter
import time
from decouple import config
import sys
import os



from google.cloud import pubsub_v1


import argparse
import time


from google.cloud import firestore

import datetime







def get_user_interactions(list_dict):
    """Crawls the targeted user's timeline and returns interactions.
    Args:
        `list_dict`, dict: A dictionary containing the following variables: 
            `search`, string: The name of the user who's timeline to search.
            `output`, list of tuples: paired list of search & interaction targets. 
            `next_query`, list: a list of names to search on the next run. 
            `limit`, int: A flag to indicate how many results should be returned. 
            'level'
    
    Functionality:
        Initialize search for the specific user.
        Get the user's tweets from their timeline. 
        Cycle through all the tweets' text and join it into a mega-string.
        Do some standardizing and replacing.
        Strip away everything except usernames, into a string. 
        Make a list of the counts, and take the top (X) most common people. 
        Creates a list of the `top` people. No duplicates 
        Tuples the results of the search & output together.
        Make search inputs for the next level of crawling.
    
    Returns:
        This function is async and has no return statement, rather it 
        instead updates the values of `output` and `next_query` extending
        the lists that were passed to it as args.
    """
    search, output, found, search_depth, level = list_dict
    
    if level > 1:
    
    
    
        project_id = os.environ['GCP_PROJECT']
        db = firestore.Client()
        get_user = db.collection(u'interactions').document(search).get()
        user_info = get_user.to_dict()
    
        if 'timestamp' in user_info:
    
    
    
            time = user_info['timestamp']
        
            d = time.strftime("%Y-%m-%d")
            d = datetime.datetime.strptime(d, "%Y-%m-%d")
            now = datetime.datetime.now()

            delta = now - d
            if delta.days < 7:
                print("User has already been checked this week.")
    		
                print('TEST CHECK DB: ', time)
                print('since: ', delta)
                return
    
    
    
    
    
    
    
    try:
        twitter_user = TWITTER.get_user(search)
        print('grabbing timeline for user: ', search)
        print('The search depth is:', search_depth)
        tweets = twitter_user.timeline(
                    count=200,
                    exclude_replies=False,
                    include_rts=True,
                    tweet_mode='extended'
        )
        full_tweets = [i.full_text for i in tweets]
        long_string = " ".join(full_tweets)
        lowercase = long_string.lower()
        remove_orgin_user = lowercase.replace(search, "")
        out = re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)',remove_orgin_user)
        
        if search_depth > 0:
            top = Counter(out).most_common(search_depth)
            interactions = []
            for interaction_count in top:
                interactions += ([interaction_count[0]] * interaction_count[1])

            tweet_data = [(search, i) for i in interactions]
            output.extend(tweet_data)

            found_users = [person[0] for person in top]
            found.extend(found_users)

        elif search_depth == -1: 
            top = Counter(out).most_common()
            tweet_data = [(search, i) for i in out]
            output = output.extend(tweet_data)
            
            found_users = [person[0] for person in top]
            found.extend(found_users)
    
    except tweepy.TweepError:
        print("tweepy.TweepError")
        
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)





def interaction_chain(origin_user, first_search_depth, second_search_depth):
    from concurrent.futures import ThreadPoolExecutor as PoolExecutor
    """Calls our async function & loops through it for each target user."""
    
    # init function variables
    data = []
    level = 0
    
    start_time = time.time()
    last_time = time.time()
    
    users_to_search = []# Next search targets




    found_users = []  # f = Found in current search.
    found_users.append(origin_user)

    past_users = []  # Current users deposited after llvl, cleans out f users.
    #past_users += origin_user
    print('test',found_users)


    # Updates the time for each loop.
    def funct_time(last, d, l):
        now = time.time()
        check_time = now - last
        print("\n\nLevel %s Completed\nLevel %s time to complete: %s." % (l, l, check_time))
        print("Level %s total cumulative interactions found:", (l, len(d)))
        return now
    
    # Dedupe & Check user list for previous runs (no duplicated work). 
    def update_lists(searched_users, found_users, past_users, level):
        found_users = list(dict.fromkeys(found_users)) # Dedupe f_users. 
        past_users += searched_users # Deposit last search(ed)_users into past_users. (input to last run)

        found_users = [x for x in found_users if x not in past_users]


        searched_users = found_users #Overwrite ss_users list with cleaned ff_users loop output. 
        found_users = [] #Reset ff_users for next run. 
        level += 1
        if level == 1: 
        	print("----------Entering %sst level. Searching the following users:----------\n" % level, searched_users)
        else: # on other runs...
            print("Level %s new connections found:" % len(searched_users), "\n\n")
            print("Total %s connections discovered so far." % (len(past_users)+len(searched_users)) )
            print("---------Beginning Level %s - Searching the following users:\n" % level, searched_users)
        return searched_users, found_users, past_users, level
    
    # Pre-run print. 
    users_to_search, found_users, past_users, level = update_lists(users_to_search, found_users, past_users, level)  
        







    # Level 1 Run.
    loop_num = 1
    with PoolExecutor(max_workers=20) as executor:
        for _ in executor.map(get_user_interactions, [(x, data, found_users, first_search_depth, level) for x in users_to_search]):
            print("Loop # ", loop_num, " . Time so far:", time.time() - start_time)
            loop_num +=1
            pass
    
    last_time = funct_time(last_time, data, level)
    users_to_search, found_users, past_users, level = update_lists(users_to_search, found_users, past_users, level) 

    # Level 2 Run.
    loop_num = 1
    with PoolExecutor(max_workers=20) as executor:
        for _ in executor.map(get_user_interactions, [(x, data, found_users, second_search_depth, level) for x in users_to_search]):
            print("Loop # ", loop_num, " . Time so far:", time.time() - start_time)
            loop_num +=1
            pass
            
            
            
    last_time = funct_time(last_time, data, level)

    users_to_search, found_users, past_users, level = update_lists(users_to_search, found_users, past_users, level)  
    
    print("Total time:", time.time() - start_time)
    print("Total Connections found:", (len(past_users)-1))
    print("Total Overall Interactions found:", len(data))
    num_total_interactions = len(data)
    print(past_users)
    return data, past_users











    

    
    
    
    

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
    
    
    
    
    
    
    
def publish(interactions, topic):
    """Publishes a message to a Pub/Sub topic."""
    # [START pubsub_quickstart_pub_client]
    # Initialize a Publisher client
    client = pubsub_v1.PublisherClient()
    # [END pubsub_quickstart_pub_client]
    # Create a fully qualified identifier in the form of
    # `projects/{project_id}/topics/{topic_name}`
    topic_path = client.topic_path('bert-optimization-testing', topic)

    # Data sent to Cloud Pub/Sub must be a bytestring

    data = json.dumps(interactions, ensure_ascii=False).encode('utf8')
    
    api_future = client.publish(topic_path, data=data)
    api_future.add_done_callback(get_callback(api_future, data))

    # Keep the main thread from exiting until background message
    # is processed.
    while api_future.running():
        time.sleep(0.1)
    
    print("data published")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


def generate_recommendation_response(original_user, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, message_id, first_search_depth=10,
                                     second_search_depth = 10):
    """
    Takes in all the established variables and passes them to the correct functions. 
    """
    # Create Twitter Connection
    twitter_auth = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),config('TWITTER_CONSUMER_SECRET'))
    
    print('Twitter Consumer Key: ', config('TWITTER_CONSUMER_KEY'))
    print('Twitter Consumer Secret: ', config('TWITTER_CONSUMER_SECRET'))
    
    #access_token = str(TWITTER_ACCESS_TOKEN)
    #access_token_secret = str(TWITTER_ACCESS_TOKEN_SECRET)
    
    access_token = config('ACCESS_TOKEN')
    access_token_secret = config('ACCESS_SECRET')
    
    
    
    
    print("Access Token: ", access_token)
    print("Access Token Secret: ", access_token_secret)

    
    
    twitter_auth.set_access_token(access_token, access_token_secret)
    global TWITTER
    TWITTER = tweepy.API(twitter_auth)

    
    
    
    original_user = str(original_user)
    output_data = [message_id]

    # Call the Multithreaded function
    response_data, users_found = interaction_chain(original_user, first_search_depth, second_search_depth)
    print("Called Multitreading Function")
    output_data.append(users_found)
    output_data.append(response_data)


    print(response_data)
    print(users_found)
    #post_to_firestore(response_data, interactions_found, original_user)
    publish(output_data, 'listen_for_interactions')





    
def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    parsed = ast.literal_eval(pubsub_message)
    print(parsed[0])
    job_id = parsed[7]
    
    publish(job_id, 'post_to_db')
    generate_recommendation_response(parsed[0], parsed[5], parsed[6], job_id)
