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
[{'tweet': {'user_id': 8496762,
   'user_name': 'tylercowen',
   'tweet': 'RT @pamela_herd: While Trump should release his tax returns, I am not thrilled that the NYT used de-identified publicly released data to do…',
   'tweet_id': '1125959002880450560',
   'bert_output': {'results': {'identity_hate': 0.00016027066158130765,
     'insult': 0.00021916520199738443,
     'obscene': 0.0001547282445244491,
     'severe_toxic': 0.0001458178012399003,
     'threat': 0.00011751330021070316,
     'toxic': 0.00033231236739084125}}}},
 {'tweet': {'user_id': 16396078,
   'user_name': 'Nate Bargatze',
   'tweet': 'RT @LargoLosAngeles: Tomorrow night is growing into a tsunami of comedy and music...joining @nickthune and #DamienJurado will be @chelseape…',
   'tweet_id': '1125957139111890944',
   'bert_output': {'results': {'identity_hate': 0.00013242011482361704,
     'insult': 0.0001986105926334858,
     'obscene': 0.00017196692351717502,
     'severe_toxic': 0.0001229296176461503,
     'threat': 9.164847142528743e-05,
     'toxic': 0.000372445210814476}}}},
 {'tweet': {'user_id': 50771088,
   'user_name': 'Mick Shaffer',
   'tweet': 'Royals bullpen all of a sudden with a 10-run, 9th-inning lead. https://t.co/S3hDSHTsM1',
   'tweet_id': '1125957060309471237',
   'bert_output': {'results': {'identity_hate': 0.00011926249862881377,
     'insult': 0.00020622869487851858,
     'obscene': 0.00017971500346902758,
     'severe_toxic': 0.00011344004451530054,
     'threat': 8.176066330634058e-05,
     'toxic': 0.0004764556942973286}}}}
     ]
```
