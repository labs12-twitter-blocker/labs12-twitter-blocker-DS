## TODO
* assess whether or not to hardcode URL's, what are alternatives


### Python code for hitting api
```import requests
from python-decouple import config
import json

#TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET saved as a .env for local testing,\
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
```[{'tweet': {'user_id': 858716964,
   'user_name': 'PFTCommenter',
   'tweet': 'Very unfootball guy move by Dabo to be in canada. Guarentee u Saban dosent even know what a passport is',
   'tweet_id': '1125941726739406848',
   'bert_output': {'results': {'identity_hate': 0.0009892451344057918,
     'insult': 0.003654920496046543,
     'obscene': 0.028357096016407013,
     'severe_toxic': 0.0008791135041974485,
     'threat': 0.0010434689465910196,
     'toxic': 0.8275536894798279}}}},
 {'tweet': {'user_id': 3363584909,
   'user_name': 'Judea Pearl',
   'tweet': 'Faculty of New York University: Oppose Academic Boycott of NYU Tel Aviv - Sign the Petition! https://t.co/yHcYCyax2A via @Change',
   'tweet_id': '1125941173887979522',
   'bert_output': {'results': {'identity_hate': 0.0009892451344057918,
     'insult': 0.003654920496046543,
     'obscene': 0.028357096016407013,
     'severe_toxic': 0.0008791135041974485,
     'threat': 0.0010434689465910196,
     'toxic': 0.8275536894798279}}}},
 {'tweet': {'user_id': 20844341,
   'user_name': 'Patrick McKenzie',
   'tweet': 'A legitimately hard question to answer: does the Bitcoin community pay more for miners to secure the blockchain via seigniorage or for informally organized web application bug bounties.\n\nNot snarking; those may be similar magnitude numbers. https://t.co/nw3VFgHPZK',
   'tweet_id': '1125941004576550912',
   'bert_output': {'results': {'identity_hate': 0.0009892451344057918,
     'insult': 0.003654920496046543,
     'obscene': 0.028357096016407013,
     'severe_toxic': 0.0008791135041974485,
     'threat': 0.0010434689465910196,
     'toxic': 0.8275536894798279}}}}]
