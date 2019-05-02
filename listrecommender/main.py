
#!pip install python-decouple
import json
import tweepy
import re
from collections import Counter
import time
from decouple import config
import pandas as pd
import numpy as np
import networkx as nx
from pandas.io.json import json_normalize

def get_user_interactions(list_dict):
    """Crawls the targeted user's timeline and returns interactions.
    Args:
        `list_dict`, dict: A dictionary containing the following variables: 
            `search`, string: The name of the user who's timeline to search.
            `output`, list of tuples: paired list of search & interaction targets. 
            `next_query`, list: a list of names to search on the next run. 
            `limit`, int: A flag to indicate how many results should be returned. 
    
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
    search, output, found, limit = list_dict
    try:
        twitter_user = TWITTER.get_user(search)
        tweets = twitter_user.timeline(
                    count=200,
                    exclude_replies=False,
                    include_rts=True,
                    tweet_mode='extended'
        )
        b = [ i.full_text for i in tweets ]
        b = " ".join(b)
        b = b.lower()
        b = b.replace(search, "")
        out = re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)',b)
        top = Counter(out).most_common(limit)

        if limit > 0:
            interactions = []
            for interaction_count in top:
                interactions += ([interaction_count[0]] * interaction_count[1])

            tweet_data = [(search, i) for i in interactions]
            output.extend(tweet_data)

            found_users = [person[0] for person in top]
            found.extend(found_users)

        elif limit == -1: 
            tweet_data = [(search, i) for i in out]
            output = output.extend(tweet_data)
            
            found_users = [person[0] for person in top]
            found.extend(found_users)
    
    except tweepy.TweepError:
        print("tweepy.TweepError")
        
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


def interaction_chain(origin_user, search_target_users, return_limit, last_lvl):
    from concurrent.futures import ThreadPoolExecutor as PoolExecutor
    """Calls our async function & loops through it for each target user."""
    
    # init function variables
    data = []
    lvl = 0
    
    start_time = time.time()
    last_time = time.time()
    
    s_users = []  # Next search targets
    f_users = search_target_users  # f = Found in current search.
    p_users = []  # Current users deposited after llvl, cleans out f users.
    p_users += origin_user # Add originating username to p_users.

    # Updates the time for each loop.
    def funct_time(last, d, l):
        now = time.time()
        check_time = now - last
        print("\n\nLevel %s Completed\nLevel %s time to complete: %s." % (l, l, check_time))
        print("Level %s total cumulative interactions found:", (l, len(d)))
        return now
    
    # Dedupe & Check user list for previous runs (no duplicated work). 
    def update_lists(ss_users, ff_users, pp_users, llvl, llst_lvl):
        ff_users = list(dict.fromkeys(ff_users)) # Dedupe f_users. 
        pp_users += ss_users # Deposit last search(ed)_users into p_users. (input to last run)
        for i in pp_users: # Remove p_users from f_users.
            a = np.array(ff_users) 
            a = a[a != i] 
            ff_users = a.tolist() 
        ss_users = ff_users #Overwrite ss_users list with cleaned ff_users loop output. 
        ff_users = [] #Reset ff_users for next run.
        if llvl == 0: # on first run.... 
            llvl += 1 
            print("----------Entering %sst level. Searching the following users:----------\n" % llvl, ss_users)
        else: # on other runs...
            print("Level %s new connections found:" % llvl, len(ss_users), "\n\n")
            print("Total %s connections discovered so far." % (len(pp_users)+len(ss_users)))
            if llvl < llst_lvl:
                llvl += 1
                print("---------Beginning Level %s - Searching the following users:\n" % llvl, ss_users)
        return ss_users, ff_users, pp_users, llvl
    
    # Pre-run print. 
    s_users, f_users, p_users, lvl = update_lists(s_users, f_users, p_users, lvl, last_lvl)  
        
    # Level 1 Run.
    loop_num = 1
    with PoolExecutor(max_workers=20) as executor:
        for _ in executor.map(get_user_interactions, [(x, data, f_users, return_limit) for x in s_users]):
            print("Loop # ", loop_num, " . Time so far:", time.time() - start_time)
            loop_num +=1
            pass
    
    last_time = funct_time(last_time, data, lvl)
    s_users, f_users, p_users, lvl = update_lists(s_users, f_users, p_users, lvl, last_lvl)  

    # Level 2 Run.
    loop_num = 1
    with PoolExecutor(max_workers=20) as executor:
        for _ in executor.map(get_user_interactions, [(x, data, f_users, return_limit) for x in s_users]):
            print("Loop # ", loop_num, " . Time so far:", time.time() - start_time)
            loop_num +=1
            pass

    last_time = funct_time(last_time, data, lvl)
    s_users, f_users, p_users, lvl = update_lists(s_users, f_users, p_users, lvl, last_lvl)  
    
    print("Total time:", time.time() - start_time)
    print("Total Connections found:", (len(p_users)-1))
    print("Total Overall Interactions found:", len(data))
    no_total_interactions = len(data)
    return data, no_total_interactions


def return_json(pageranked_df, origin_user, search_target_users,
                qty_users_found, qty_interactions_found, api_used,no_of_results):
    ranked_dict = pageranked_df[["username"]].head(no_of_results).username.tolist()
    #search_dict = {("search_user_%s" % i) : search_target_users[i] for i in range(0, len(search_target_users))}
    final_dict = {"original_user" : origin_user, 
                  "search_users" : search_target_users, 
                  "network_size": qty_users_found,
                  "interactions_found" : qty_interactions_found, 
                  "ranked_results": ranked_dict,
                  "api_usage": api_used}
    final_json = json.dumps(final_dict)
    return final_json # Returns JSON string. 


def generate_recommendation_response(original_user, search_users, return_limit,
                                     last_level,no_of_results,
                                     TWITTER_ACCESS_TOKEN,
                                     TWITTER_ACCESS_TOKEN_SECRET):
    """
    Takes in all the established variables and passes them to the correct functions. 
    """
    # Create Twitter Connection
    twitter_auth = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),config('TWITTER_CONSUMER_SECRET'))
    access_token = TWITTER_ACCESS_TOKEN
    access_token_secret = TWITTER_ACCESS_TOKEN_SECRET
    twitter_auth.set_access_token(access_token, access_token_secret)
    global TWITTER
    TWITTER = tweepy.API(twitter_auth)

    # Capture API rate limit status
    start_api_check = TWITTER.rate_limit_status()
    limits_alpha = json_normalize(start_api_check)

    # Call the Multithreaded function
    response_data, interactions_found = interaction_chain(original_user, search_users, return_limit, last_level)
    print("Called Multitreading Function")

    # DF before Groupby (Turn response data into pandas df)
    df = pd.DataFrame(response_data, 
                      columns=['source_user', 'interaction_user'])

    # Create groupby counts
    df_group = (df.groupby(['source_user','interaction_user'])
                  .size().reset_index().rename(columns={0: "count"}))

    # Create "Normalized" interaction weights for each user's interactions. 
    a = df_group.groupby('source_user')['count'].transform('sum')
    df_group['weight'] = df_group['count'].div(a)
    print("normalized data via groupby")

    # Create the directional graph object. 
    # (Uses weight or count derived summaries.)
    DG = nx.from_pandas_edgelist(df_group, "source_user", "interaction_user",
                                edge_attr=['weight', "count"], 
                                create_using=nx.DiGraph())
    found_nodes = nx.number_of_nodes(DG)
    print("converted df to graph with %s nodes", found_nodes)

    # Pagerank it!
    pr = nx.pagerank_numpy(DG, alpha= 0.85, weight="weight") 
    dg_pr_df = pd.DataFrame([pr]).T.reset_index() 
    dg_pr_df = dg_pr_df.rename(index=str, columns={"index": "username", 0: "pagerank"})
    dg_pr_df = dg_pr_df.sort_values(by=['pagerank'], ascending=False)
    print("pageranked the values")

    # REWRITE AS FUNCTION >>>>>>>
    # Query API to get status update
    end_api_check = TWITTER.rate_limit_status()
    limits_beta = json_normalize(end_api_check).T
    limits_beta.rename(columns = {0:'beta',}, inplace = True)

    # Compare the change of ALL API ENDPOINTS between limits, alpha (before run), and beta (after run.)
    limits_delta = limits_alpha.T.copy()
    limits_delta['beta'] = limits_beta['beta']
    limits_delta = limits_delta.reset_index(drop=False)
    limits_delta.rename(columns = {0:'alpha', 'index':'api_endpoint'}, inplace = True)
    limits_delta = limits_delta[['api_endpoint','alpha', 'beta']].assign(delta=limits_delta.alpha != limits_delta.beta)
    limits_delta['type'] = limits_delta.api_endpoint.str.split(pat = '.', n = 1, expand = True)[0]
    limits_delta['sub_type'] = limits_delta.api_endpoint.str.split(pat = '.', n = 2, expand = True)[1]
    limits_delta['api_path'] = limits_delta.api_endpoint.str.split(pat = '.', n = 2, expand = True)[2].str.rsplit(pat = '.', n = 1, expand = True)[0]
    limits_delta['method'] = limits_delta.api_path.str.rsplit(pat = '/', n = 1, expand = True)[1]
    limits_delta['stat'] = limits_delta.api_endpoint.str.rsplit(pat = '.', n = 1, expand = True)[1]
    limits_delta['alpha'] = pd.to_numeric(limits_delta["alpha"], errors='coerce')
    limits_delta['beta'] = pd.to_numeric(limits_delta["beta"], errors='coerce')
    limits_delta = limits_delta[['type', 'sub_type', 'api_path', 'method', 'stat', 'alpha', 'beta', 'delta']]
    limits_delta["amt_used"] = limits_delta["alpha"] - limits_delta["beta"]

    # Filter Dataframe
    api_usage = limits_delta[(limits_delta['stat'].str.contains("reset") == False) & (limits_delta['delta']==True)]
    api_usage = api_usage[["sub_type", "api_path", "alpha", "beta", "amt_used"]].copy()
    api_usage.rename(columns = {"sub_type": "type", 'alpha': "before_query", 'beta':'after_query'}, inplace = True)
    api_usage = api_usage.set_index('type')
    api_usage = api_usage.to_dict('index')
    # REWRITE AS FUNCTION <<<<<<<<
    print("calculated API usage %s", api_usage)

    # Return the final output. 
    output = return_json(dg_pr_df, original_user, search_users, found_nodes, interactions_found, api_usage, no_of_results)

    return output


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
        # original_user check/set/error
        if request_json and 'original_user' in request_json:
            original_user = request_json['original_user']
        else:
            raise ValueError("Invalid JSON, or missing a 'original_user'")
        # search_users check/set/error
        if request_json and 'search_users' in request_json:
            search_users = request_json['search_users']
        else:
            raise ValueError("JSON is invalid, or missing a 'search_users'")
        # return_limit check/set/error
        if request_json and 'return_limit' in request_json:
            return_limit = request_json['return_limit']
        else:
            raise ValueError("JSON is invalid, or missing a 'return_limit'")
        # last_level check/set/error
        if request_json and 'last_level' in request_json:
            last_level = request_json['last_level']
        else:
            raise ValueError("JSON is invalid, or missing a 'last_level'")
        # no_of_results check/set/error
        if request_json and 'no_of_results' in request_json:
            no_of_results = request_json['no_of_results']
        else:
            raise ValueError("JSON is invalid, or missing a 'no_of_results'")
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
            return generate_recommendation_response(original_user, search_users,
                                                    return_limit,
                                                    last_level,no_of_results,
                                                    TWITTER_ACCESS_TOKEN,
                                                    TWITTER_ACCESS_TOKEN_SECRET)
    else:
        return abort(405)