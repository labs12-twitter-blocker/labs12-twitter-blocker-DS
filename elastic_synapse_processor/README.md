# Elastic Synapse Processor
![img](https://i.imgur.com/VfvCPuH.jpg)

____



Table of Contents
=================

* [Elastic Synapse Processor](#elastic-synapse-processor)
* [API Usage:](#api-usage)
    * [Available Endpoints:](#available-endpoints)
      * [Toxic Comments TODO: ADD ENDPOINT INSTRUCTIONS](#toxic-comments-todo-add-endpoint-instructions)
* [Development:](#development)
    * [Development Pre\-Requisites:](#development-pre-requisites)
* [Model Training and Deployment Pipeline (From Scratch):](#model-training-and-deployment-pipeline-from-scratch)
    * [1\. Model Training:](#1-model-training)
      * [TODO : ADD FURTHER DETAILS/INSTRUCTION](#todo--add-further-detailsinstruction)
    * [2\. Create Container For Model (Run these commands in Google Cloud Services Console)](#2-create-container-for-model-run-these-commands-in-google-cloud-services-console)
      * [Login with Docker](#login-with-docker)
      * [Name of docker image to update/create](#name-of-docker-image-to-updatecreate)
      * [Version for docker image \- NOTE to update a model this must get incremented](#version-for-docker-image---note-to-update-a-model-this-must-get-incremented)
      * [Tensorflow Serving Model Name \- NOTE this should always stay 'bert'](#tensorflow-serving-model-name---note-this-should-always-stay-bert)
      * [Put your docker user here](#put-your-docker-user-here)
      * [To use a different model change the path \- NOTE this should point to a Saved\_Model\.pb and variables folder\.](#to-use-a-different-model-change-the-path---note-this-should-point-to-a-saved_modelpb-and-variables-folder)
    * [3\. Create Container for Flask Client( Run these commands in Google Cloud Services Console)](#3-create-container-for-flask-client-run-these-commands-in-google-cloud-services-console)
      * [Note: You can use a custom repo here, but it must be a fork from chrisseiler96/bert\-client\-server\-tests](#note-you-can-use-a-custom-repo-here-but-it-must-be-a-fork-from-chrisseiler96bert-client-server-tests)
      * [This includes necessary files for creating docker container/dependencies\.](#this-includes-necessary-files-for-creating-docker-containerdependencies)
    * [4\. Create Project Google Cloud Services](#4-create-project-google-cloud-services)
    * [5\. Create new Kubernetes Cluster on Google Cloud Services](#5-create-new-kubernetes-cluster-on-google-cloud-services)
    * [6\. Deploy To Kubernetes/Google Cloud Services](#6-deploy-to-kubernetesgoogle-cloud-services)
      * [Run these commands locally](#run-these-commands-locally)
* [Add ML Endpoint](#add-ml-endpoint)
* [Update Client](#update-client)
* [Useful Commands](#useful-commands)
* [Debug](#debug)


## API Usage: 
### Available Endpoints:
#### Toxic Comments TODO: ADD ENDPOINT INSTRUCTIONS









## Development:
  ### Development Pre-Requisites:
  * Google Cloud Services Account
  * Google Cloud Bucket
  * Dockerhub Account
  * Kompose (link to kompose DL)
  * Google Cloud SDK (link to SDK)
  



## Model Training and Deployment Pipeline (From Scratch):

### 1. Model Training: 
  https://colab.research.google.com/drive/1X2zP-C3os4vt0jlJ_OQ_u5kq6pGErPd3
  #### TODO : ADD FURTHER DETAILS/INSTRUCTION
  
____
  
### 2. Create Container For Model (Run these commands in Google Cloud Services Console)
____

#### Login with Docker
`docker login`

#### Name of docker image to update/create
`IMAGE_NAME=tf_serving_bert_toxic`  

#### Version for docker image - NOTE to update a model this must get incremented
`VER=1556822021_v5`

#### Tensorflow Serving Model Name - NOTE this should always stay 'bert'
`MODEL_NAME=bert`

#### Put your docker user here
`DOCKER_USER=       {your docker user} `

```
cd ~
docker run -d --name $IMAGE_NAME tensorflow/serving
mkdir ~/models
```

#### To use a different model change the path - NOTE this should point to a Saved_Model.pb and variables folder.
`gsutil cp -r  gs://not-another-bert-bucket/bert/export/multilabel/1556822021 ~/models`

```
docker cp ~/models $IMAGE_NAME:/models/$MODEL_NAME
docker commit --change "ENV MODEL_NAME $MODEL_NAME" $IMAGE_NAME $DOCKER_USER/$IMAGE_NAME
docker tag $DOCKER_USER/$IMAGE_NAME $DOCKER_USER/$IMAGE_NAME:$VER
docker push $DOCKER_USER/$IMAGE_NAME:$VER
```
 
____

### 3. Create Container for Flask Client( Run these commands in Google Cloud Services Console)
____


#### Note: You can use a custom repo here, but it must be a fork from chrisseiler96/bert-client-server-tests
#### This includes necessary files for creating docker container/dependencies.
```
git clone https://github.com/chrisseiler96/bert-client-server-tests.git

cd ~/bert-client-server-tests

CLIENT_IMAGE_NAME=bert_toxic_client
CLIENT_VER=v5
docker build -t $DOCKER_USER/$CLIENT_IMAGE_NAME .
docker tag $DOCKER_USER/$CLIENT_IMAGE_NAME $DOCKER_USER/$CLIENT_IMAGE_NAME:$CLIENT_VER
docker push $DOCKER_USER/$CLIENT_IMAGE_NAME:$CLIENT_VER
 ```
 
### 4. Create Project Google Cloud Services

### 5. Create new Kubernetes Cluster on Google Cloud Services
  
### 6. Deploy To Kubernetes/Google Cloud Services
  #### Run these commands locally
  ```
  gcloud config set container/cluster bert-cluster
gcloud container clusters get-credentials bert-cluster --zone us-east1-b --project bert-239819
kompose convert --stdout | kubectl apply -f -

# get service IPs
kubectl get service 
```
  
# Add ML Endpoint

# Update Client


# Useful Commands

# Debug





