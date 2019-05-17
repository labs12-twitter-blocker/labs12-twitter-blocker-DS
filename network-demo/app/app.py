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


def get_network(user):
    headers = {"Content-Type": "application/json"}
    body = {
        "TWITTER_ACCESS_TOKEN": config("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": config("TWITTER_ACCESS_TOKEN_SECRET"),
        "search": user,
    }
    edge_list = requests.post(
        url="https://us-central1-twitter-bert-models.cloudfunctions.net/function-1",
        headers=headers,
        data=json.dumps(body),
    )
    edge_list = edge_list.json()
    edge_df = pd.DataFrame(edge_list, columns=["source", "target"])
    # create a graph and add edges
    DG = nx.MultiGraph()
    DG = nx.from_pandas_edgelist(edge_df, "source", "target")
    DG_layout = nx.spectral_layout(DG)

    # create json nodes from graph
    sl_nodes = nx.spectral_layout(DG)
    node_list = list(sl_nodes)
    node_x = [sl_nodes[i][0] for i in node_list]
    node_y = [sl_nodes[i][1] for i in node_list]
    node_x = json.dumps(node_x)
    node_y = json.dumps(node_y)

    node_counter = Counter(list(chain.from_iterable(edge_list)))
    node_keys = list(sl_nodes.keys())
    node_weights = [node_counter[i] for i in node_keys]
    node_weights = json.dumps(node_weights)
    node_list = json.dumps(node_list)

    # create json edges from graph
    edges = list(DG.edges.data())
    sl_edges_x = []
    sl_edges_y = []
    sl_edges_weight = []
    for i in range(len(edges)):
        sl_edges_x.append(sl_nodes[edges[i][0]][0])
        sl_edges_y.append(sl_nodes[edges[i][0]][1])
        sl_edges_x.append(sl_nodes[edges[i][1]][0])
        sl_edges_y.append(sl_nodes[edges[i][1]][1])
        sl_edges_x.append("")
        sl_edges_y.append("")
        sl_edges_weight.append("")
    x = json.dumps(sl_edges_x)
    y = json.dumps(sl_edges_y)
    weights = json.dumps(sl_edges_weight)

    user = json.dumps(user)

    #         return render_template("network.html", edge_x =x, edge_y =y, node_x =
    #         node_x, node_y =node_y, user = user, node_list=node_list,
    #         node_weights=node_weights)
    return x, y, node_x, node_y, user, node_list, node_weights


def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def root():
        return render_template("root.html")

    @app.route("/network", methods=["GET"])
    def network():
        user = request.values["user"]
        user = user.replace("@", "")
        x, y, node_x, node_y, user, node_list, node_weights = get_network(user)
        return render_template(
            "network.html",
            edge_x=x,
            edge_y=y,
            node_x=node_x,
            node_y=node_y,
            user=user,
            node_list=node_list,
            node_weights=node_weights,
        )

    return app
