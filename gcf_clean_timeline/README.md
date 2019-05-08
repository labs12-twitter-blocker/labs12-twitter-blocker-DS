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
[{'user_id': 20178419,
  'user_name': 'Charlie Warzel',
  'tweet': 'Wanted to share this from a reader who fought to bring broadband internet to her rural area. Privacy fears have her questioning the promise of the technology in the first place. \nhttps://t.co/rQFAzedSsy https://t.co/sWQ4tVR0nL',
  'tweet_id': '1125942774870626304',
  'bert_output': {'results': {'identity_hate': 0.00014293211279436946,
    'insult': 0.00020261162717361003,
    'obscene': 0.00015373028873000294,
    'severe_toxic': 0.00013324874453246593,
    'threat': 0.00010578848741715774,
    'toxic': 0.00031644446426071227}}},
 {'user_id': 858716964,
  'user_name': 'PFTCommenter',
  'tweet': 'Very unfootball guy move by Dabo to be in canada. Guarentee u Saban dosent even know what a passport is',
  'tweet_id': '1125941726739406848',
  'bert_output': {'results': {'identity_hate': 9.91309862001799e-05,
    'insult': 0.00024265862884931266,
    'obscene': 0.0002427479630568996,
    'severe_toxic': 9.135981963481754e-05,
    'threat': 5.7972181821241975e-05,
    'toxic': 0.0008805064135231078}}}]
```
