from flask import Flask, request, render_template, jsonify, json
from decouple import config
from flask_cors import CORS
import numpy as np
import networkx as nx
import tweepy
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import re
from collections import Counter
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
	return [ i[0] for i in Counter(index).most_common(10) ]


def get_first_user_connections(search, interactions_list):
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
	interactions = " ".join(interactions)
	interactions_list.append(interactions)
	return interactions_list





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
		for i in index:
			 get_first_user_connections(i, interactions_list)
		#add first item to the top of the list

		#turn the interactions into a dataframe
		vectorizer = CountVectorizer(min_df=2)
		X = vectorizer.fit_transform(interactions_list)
		display_df = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names(), index=index)
		#create a graph and add edges
		DG = nx.MultiGraph()
		for i in display_df.index.values:
			for j in display_df.columns:
				if display_df[j].loc[i] > 0:
					DG.add_edge(j,i,weight = np.sqrt(display_df[j].loc[i] ))
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
				return int(display_df[i].sum())
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
