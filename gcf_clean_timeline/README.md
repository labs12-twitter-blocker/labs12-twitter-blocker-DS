# Clean Timeline
This subdirectory has one purpose, to show the toxicity of each tweet in a logged-in user's timeline.

Hit the url with a POST request and the proper credentials and the function will output some important tweet metadata and the BERT model output

Run time ~ 11 seconds * num_pages.
## TODO
* assess whether or not to hardcode URL's, what are alternatives?


### Python code for hitting api
##### 2 types of possible requests. With and without 'since_id'
```import requests
from python-decouple import config
import json

#TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET saved as a .env for local testing,
#pass it some other way for production.

headers = {"Content-Type":"application/json"}
body = {"TWITTER_ACCESS_TOKEN": config('TWITTER_ACCESS_TOKEN'),
        "TWITTER_ACCESS_TOKEN_SECRET": config('TWITTER_ACCESS_TOKEN_SECRET')
        }
r = requests.post("https://us-central1-twitter-bert-models.cloudfunctions.net/function-2",
                  headers=headers,
                  data=json.dumps(body))
```

```import requests
from python-decouple import config
import json
headers = {"Content-Type":"application/json"}
body = {"TWITTER_ACCESS_TOKEN": config('TWITTER_ACCESS_TOKEN'),
        "TWITTER_ACCESS_TOKEN_SECRET": config('TWITTER_ACCESS_TOKEN_SECRET'),
	"num_pages":2,
	"toxicity_threshold":0.8
        }
r = requests.post("https://us-central1-twitter-bert-models.cloudfunctions.net/function-1",
                  headers=headers,
                  data=json.dumps(body))
```
### Returns
Function returns a full tweet object and the bert result. For more information on the tweet object, please use https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/intro-to-tweet-json.
*This is a modified result intended to illustrate shape of the bert result*
``` {
	"results":[
	    {
            "tweet": {
                ...
                "full_text": "@DstarDev Go and boil your bottoms, sons of a silly person. 
		I blow my nose at you, so-called Arthur-king, you and all your silly English
		...you empty headed animal food trough wiper!...... 
		I fart in your general direction! . Your mother was a hamster and 
		your father smelt of elderberries! https://t.co/Txb3QaXys3",
                ...
            },
            "bert_result": {
                "identity_hate": 0.005,
                "insult": 0.9892,
                "obscene": 0.1273,
                "severe_toxic": 0.0022,
                "threat": 0.0011,
                "toxic": 0.9495
            }
        },
   ...
   ]
```
