# Clean Timeline
This subdirectory has one purpose, to show the toxicity of each tweet in a logged-in user's timeline.

Hit the url with a POST request and the proper credentials and the function will output some important tweet metadata and the BERT model output

Run time ~ 31 seconds for 20 tweets
## TODO
* assess whether or not to hardcode URL's, what are alternatives?


### Python code for hitting api
```import requests
from python-decouple import config
import json

#TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET saved as a .env for local testing,
#pass it some other way for production.

headers = {"Content-Type":"application/json"}
body = {"TWITTER_ACCESS_TOKEN": config('TWITTER_ACCESS_TOKEN'),
        "TWITTER_ACCESS_TOKEN_SECRET": config('TWITTER_ACCESS_TOKEN_SECRET')
        }
r = requests.post("https://us-central1-twitter-bert-models.cloudfunctions.net/function-1",
                  headers=headers,
                  data=json.dumps(body))
```
### Returns
*returning only 2 examples for brevity*
``` 
{'tweet': {'tweet': {'user_id': 858716964,
    'user_name': 'PFTCommenter',
    'tweet': 'Dan marino of planet’s. V sad',
    'tweet_id': '1126657772106461187'}},
  'bert_result': {'identity_hate': 6.970763206481934e-05,
   'insult': 0.00017696619033813477,
   'obscene': 0.00011560320854187012,
   'severe_toxic': 5.3554773330688477e-05,
   'threat': 5.4776668548583984e-05,
   'toxic': 0.0004666149616241455}},
 {'tweet': {'tweet': {'user_id': 858716964,
    'user_name': 'PFTCommenter',
    'tweet': 'Saturn Jupter Neptune and Uranus have rings though. Earth hasnt won shit https://t.co/fYhmlyUpd4',
    'tweet_id': '1126657331260002304'}},
  'bert_result': {'identity_hate': 0.0005328953266143799,
   'insult': 0.0031661689281463623,
   'obscene': 0.8130886554718018,
   'severe_toxic': 0.0009493827819824219,
   'threat': 0.00034987926483154297,
   'toxic': 0.766826868057251}}
   ...
   ]
```
