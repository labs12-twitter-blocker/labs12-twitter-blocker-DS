# Tweet-Blocker Readme
## Setting up the python dev environment:
The python dev environment setup guide can be followed here 
https://cloud.google.com/python/setup

#### Navigate to the app folder: 
`cd tweet-blocker`

#### Create a new virtual env:
`virtualenv --python python3 env`

#### Create the virtualenv:
`source env/bin/activate`

#### This will reproduce the Google Cloud Function Environment:
`pip install -r cloud_functions_env.txt`

#### This will stop the environment:
`deactivate`


## Adding new packages: 
Packages for cloud functions can be pinned/initialized via the requirements.txt

Packages that we don't want to have to load or install can be added to the repo by using the `pip install` command  with the `-t packages` flag to install the dependencies into our `packages` folder.

### Copy your dependency into a local directory:

* ```pip install -t packages DEPENDENCY```

* Import from this module to use your dependency:
    ```import DIRECTORY.DEPENDENCY```