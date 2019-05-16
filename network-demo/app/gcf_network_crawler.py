from flask import abort
from decouple import config
import tweepy
from collections import Counter
import asyncio
from concurrent.futures import ThreadPoolExecutor
import nest_asyncio
nest_asyncio.apply()


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

    content_type = request.headers["content-type"]
    request_json = request.get_json(silent=True)
    request_args = request.args

    if content_type == "application/json":
        request_json = request.get_json(silent=True)
        # TWITTER_ACCESS_TOKEN check/set/error
        if request_json and "TWITTER_ACCESS_TOKEN" in request_json:
            TWITTER_ACCESS_TOKEN = request_json["TWITTER_ACCESS_TOKEN"]
        else:
            raise ValueError("Missing a 'TWITTER_ACCESS_TOKEN'")
        # TWITTER_ACCESS_TOKEN_SECRET check/set/error
        if request_json and "TWITTER_ACCESS_TOKEN_SECRET" in request_json:
            TWITTER_ACCESS_TOKEN_SECRET = request_json["TWITTER_ACCESS_TOKEN_SECRET"]
        else:
            raise ValueError("Missing a 'TWITTER_ACCESS_TOKEN_SECRET'")

        if request_json and "num_pages" in request_json:
            num_pages = request_json["num_pages"]
        else:
            num_pages = 1

        # Call the function for the POST request.
        if request.method == "POST":
            establish_twitter_credentials(TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)
            return main(num_pages)
    else:
        return abort(405)

def establish_twitter_credentials(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET):
    """establish Twitter as as global. No need to pass it everytime.
    """
    twitter_auth = tweepy.OAuthHandler(
        config("TWITTER_CONSUMER_KEY"), config("TWITTER_CONSUMER_SECRET")
    )
    access_token = TWITTER_ACCESS_TOKEN
    access_token_secret = TWITTER_ACCESS_TOKEN_SECRET
    twitter_auth.set_access_token(access_token, access_token_secret)
    global TWITTER
    TWITTER = tweepy.API(twitter_auth)
    
def main(search):
    """
    1. Establish the edge_list as an empty list
    2. Call the two executor functions, updating & passing the edge_list as it goes
    3. Return the edge_list
    """
    edge_list = []
    edge_list, top_interactions = execute_async_input_user_event_loop(search, edge_list)
    edge_list = execute_async_interactions_event_loop(top_interactions, edge_list)
    return edge_list


def execute_async_input_user_event_loop(search, edge_list):
    """
    This function does something analogous to compiling the get_data_asynchronously function,
    Then it executes loop.
    1. Call the get_data_function
    2. Get the event_loop
    3. Run the tasks (Much easier to understand in python 3.7, "ensure_future" was changed to "create_task")
    4. Edge_list and top_interactions will be passed to the next functions
    """
    future = asyncio.ensure_future(get_input_user_data_asynchronous(search, edge_list))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    return edge_list, top_interactions


async def get_input_user_data_asynchronous(search, edge_list):
    """
    1. Establish an executor and number of workers
    2. Establish the session
    3. Establish the event loop
    4. Create the tasks. Add two lists together. (because as I understand appending adds the list inside of a list.)
        4a. tasks are created by list comprenhensions
    5. Gather tasks.
    """
    with ThreadPoolExecutor(max_workers=20) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor, get_user_timeline, *(session, search, edge_list, page)
                )
                for page in range(10)
            ] + [
                loop.run_in_executor(
                    executor, get_user_favorites, *(session, search, edge_list, page)
                )
                for page in range(10)
            ]
            for response in await asyncio.gather(*tasks):
                pass


def get_user_timeline(session, search, edge_list, page):
    """
    1. Get 200 user tweets
    2. Use a necessarily complex list comprehension to put each individual name mentioned in a tweet into a list
    3. make and return the edge_list: a list of tuples of the (search user, interaction)
    4. make and return the top_interactions: a list of top interactions using the python Counter function
    """
    timeline = TWITTER.user_timeline(
        id=search,
        count=200,
        exclude_replies=False,
        include_rts=True,
        tweet_mode="extended",
        page=page,
    )
    timeline = [
        user_mentions["screen_name"]
        for um_list in [tweet.entities["user_mentions"] for tweet in timeline]
        for user_mentions in um_list
    ]
    # timeline = [i for sublist in timeline for i in sublist]
    edge_list += [(search, i) for i in timeline]
    global top_interactions
    top_interactions = [i for i in Counter(timeline).most_common(10)]
    top_interactions = [i[0] for i in top_interactions]
    return top_interactions, edge_list


def get_user_favorites(session, search, edge_list, page):
    """
    1. Get 200 user favorites
    2. Extract the author from each favorited tweet.
    3. Make and return the edge_list: a list of tuples of the (search user, interaction)
    """
    timeline = TWITTER.favorites(
        id=search,
        count=200,
        exclude_replies=False,
        include_rts=True,
        tweet_mode="extended",
        page=page,
    )
    timeline = [tweet.author.screen_name for tweet in timeline]
    edge_list += [(i, search) for i in timeline]
    return edge_list


def execute_async_interactions_event_loop(top_interactions, edge_list):
    """This function does something analogous to compiling the get_data_asynchronously function,
    Then it executes loop."""
    future = asyncio.ensure_future(
        get_interactions_data_asynchronous(top_interactions, edge_list)
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    return edge_list


async def get_interactions_data_asynchronous(top_interactions, edge_list):
    """
    1. Establish an executor and number of workers
    2. Establish the session
    3. Establish the event loop
    4. Create the tasks. Add two lists together. (because as I understand appending adds the list inside of a list.)
        4a. tasks are created by list comprenhensions
    5. Gather tasks.
    """
    with ThreadPoolExecutor(max_workers=20) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor, get_user_timeline, *(session, search, edge_list, 1)
                )
                for search in top_interactions
            ] + [
                loop.run_in_executor(
                    executor, get_user_favorites, *(session, search, edge_list, 1)
                )
                for search in top_interactions
            ]
            for response in await asyncio.gather(*tasks):
                pass
