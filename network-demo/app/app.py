from flask import Flask, request, render_template, jsonify, json
from decouple import config
from flask_cors import CORS
import numpy as np
import requests
import networkx as nx
import tweepy
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import re
from collections import Counter
import asyncio
from concurrent.futures import ThreadPoolExecutor
import nest_asyncio
nest_asyncio.apply()

#set up twitter environment
TWITTER_AUTH =tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)


def get_first_user_interactions(search,index):
    twitter_user =TWITTER.get_user(search)
    tweets = twitter_user.timeline(
				count =200,
				exclude_replies = False,
				include_rts=True,
				tweet_mode='extended'
				)
    # generate a  list of tweets. join it to string. extract user names. turn
    # it into a string again.
    #b is a transistion variable
    b = [ i.full_text for i in tweets ]
    b = " ".join(b)
    b = b.lower()
    b = b.replace(search, "")
    #regex for extracting @twitter_handles as elements of a list
    index=re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)',b)
        # return the most common  names
    return [ i[0] for i in Counter(index).most_common(25) ]


def get_first_user_connections_multi_process(session,search,
        interactions_list,index):
    try:
        twitter_user =TWITTER.get_user(search)
        tweets = twitter_user.timeline(
                        count =200,
                        exclude_replies = False,
                        include_rts=True,
                        tweet_mode='extended'
                        )
        #b is a transistion variable
        b = [ i.full_text for i in tweets ]
        b = " ".join(b)
        b = b.lower()
        b = b.replace(search, "")
        #regex for extracting @twitter_handles as elements of a list
        interactions = re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)',b)
        # turn the list to string and add it to a list
        interactions =" ".join(interactions)
        interactions_list.append(interactions)
    except:
       index.remove(search)
    finally:
        return index,interactions_list
async def get_data_asynchronous(index,interactions_list):
    with ThreadPoolExecutor(max_workers =40) as executor:
        with requests.Session() as session:
            #initialize the event loop
            loop = asyncio.get_event_loop()

            #create a list of tasks with list comprehension.
            #The executor function will run
            #get_first_user_connections_multi_process
            tasks = [ loop.run_in_executor(
                executor, get_first_user_connections_multi_process,*(session, i,
                    interactions_list, index) ) for i in index]
            #initialize the tasks to run and await the result
            for response in await asyncio.gather(*tasks):
                pass

def execute_async_event_loop(index, interactions_list):
    """this function does something analogous to compiling the
    get_data_asynchronously  function and executes it.
    """
    asyncio.set_event_loop(asyncio.new_event_loop())
    future = asyncio.ensure_future(get_data_asynchronous(index,
        interactions_list))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)

    return index, interactions_list

def create_app():
    app = Flask(__name__)
    CORS(app)


    @app.route('/')
    def root():
        return render_template("root.html")

    @app.route('/network', methods = ["GET"])
    def get_network():
        user = request.values["user"]
        user = user.replace("@","")
        interactions_list = []
        index = []
        index = get_first_user_interactions(user,index)
        index = list(set([user] +index))
        index, interactions_list = execute_async_event_loop(index, interactions_list)

        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(interactions_list)
        df = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names(),index= index)
        DG = nx.MultiGraph()
        for i in df.index.values:
            for j in df.columns:
                if df[j].loc[i] >0:
                    DG.add_edge(j,i,weight = np.sqrt(df[j].loc[i] ))
                else:
                    pass
        #create json nodes from graph
        sl_nodes = nx.spectral_layout(DG)
        node_list = list(sl_nodes)
        node_x = [sl_nodes[i][0] for i in node_list]
        node_y = [sl_nodes[i][1] for i in node_list]
        node_x = json.dumps(node_x)
        node_y = json.dumps(node_y)
        def get_column_sum(i):
            try:
                return int(df[i].sum())
            except:
                return 1
        node_weights = [ get_column_sum(i) for i in node_list ]
        node_weights = json.dumps(node_weights)
        node_list = json.dumps(node_list)

        #create json edges from graph
        edges = list(DG.edges.data())
        sl_edges_x = []
        sl_edges_y = []
        sl_edges_weight = []
        for i in range(len(edges)):
            sl_edges_x.append(sl_nodes[edges[i][0]][0])
            sl_edges_y.append(sl_nodes[edges[i][0]][1])
            sl_edges_x.append(sl_nodes[edges[i][1]][0])
            sl_edges_y.append(sl_nodes[edges[i][1]][1])
            sl_edges_weight.append(edges[i][2]["weight"])
            sl_edges_weight.append(edges[i][2]["weight"])
            sl_edges_x.append("")
            sl_edges_y.append("")
            sl_edges_weight.append("")
        x = json.dumps(sl_edges_x)
        y = json.dumps(sl_edges_y)
        weights = json.dumps(sl_edges_weight)

        user = json.dumps(user)
        return render_template("network.html", edge_x =x, edge_y =y, node_x =
        node_x, node_y =node_y, user = user, node_list=node_list,
        node_weights=node_weights)



    return app
