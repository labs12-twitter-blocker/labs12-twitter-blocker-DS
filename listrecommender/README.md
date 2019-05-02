# DS List Recommender API Endpoint
#### Type:
**POST**

#### Endpoint address:
https://us-central1-twitter-follower-blocker.cloudfunctions.net/list_rec

#### Headers: 
```[{"key":"Content-Type","name":"Content-Type","value":"application/json","description":"Flag that the body is JSON. ","type":"text"}]```

#### Body: 
*JSON(application/json)*
```
{
    "original_user": "bwinterrose",
    "TWITTER_ACCESS_TOKEN": "<ACCESS TOKEN >",
    "TWITTER_ACCESS_TOKEN_SECRET": "<ACCESS TOKEN SECRET>",
    "search_users": [
        "austen",
        "paulg",
        "justinkhan",
        "tommycollison",
        "lambdaschool"
    ],
    "return_limit": 20,
    "last_level": 2,
    "no_of_results": 50
}
```

#### Time 
Current time to process is around 36 seconds. 
