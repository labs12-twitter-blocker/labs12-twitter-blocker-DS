<h1 align="center">Elastic Synapse Processor</h1>



<p align="center">
    <img src="https://github.com/chrisseiler96/gitignore/blob/master/9q0v.gif?raw=true" wwidth=480 height=360.000>
</p>

<p align="center"> This repository describes the architecture and development of the Elastic Synapse Processer (ESP). 
</p>

____

<h2 align="center">What is it?</h2>




The Elastic Synapse Processor is a framework for quickly creating and deploying Neural Network endpoints in an effiecient pipeline suited to scale for enterprise applications.

The Elastic Synapse Processor is designed around [Google's BERT](https://github.com/google-research/bert) and makes use of transfer learning to quickly reach state of the art performance on new language processing tasks. The use of transfer learning also reduces the amount of training data required to create highly performant models.



Table of Contents
=================

* [API Usage:](#api-usage)
    * [Available Endpoints:](#available-endpoints)
* [Development:](#development)
    * [Development Pre\-Requisites:](#development-pre-requisites)
* [Model Training and Deployment Pipeline (From Scratch):](#model-training-and-deployment-pipeline-from-scratch)
    * [1\. Model Training:](#1-model-training)
    * [2\. Create Container For Model](#2-create-container-for-model-run-these-commands-in-google-cloud-services-console)
    * [3\. Create Container for Flask Client](#3-create-container-for-flask-client-run-these-commands-in-google-cloud-services-console)
    * [4\. Deploy To Kubernetes/Google Cloud Services](#6-deploy-to-kubernetesgoogle-cloud-services)
* [Add ML Endpoint](#add-ml-endpoint)
* [Update Client](#update-client)
* [Useful Commands](#useful-commands)
* [Debug](#debug)


## Development Flow
![img](https://i.imgur.com/VfvCPuH.jpg)

## API Usage: 
### Available Endpoints:
#### Toxic Comments Endpoint 
![img2](https://i.imgur.com/epVS7Hf.png)
##### TODO: ADD INSTRUCTIONS








## Development:
  ### Development Pre-Requisites:
  * Google Cloud Services Account
  * Google Cloud Bucket
  * Dockerhub Account
  * Kompose (https://github.com/kubernetes/kompose)
  * Google Cloud SDK (https://cloud.google.com/sdk/)
  



## Model Training and Deployment Pipeline (From Scratch):

### Before Beginning: 
* Create new Kubernetes Cluster on Google Cloud Service
* Create Project Google Cloud Services    

____

### 1. Model Training: 
  https://colab.research.google.com/drive/1X2zP-C3os4vt0jlJ_OQ_u5kq6pGErPd3
  #### TODO : ADD FURTHER DETAILS/INSTRUCTION
  
____
  
### 2. Create Container For Model
#### (Run these commands in Google Cloud Services Console)
____

#### Login with Docker
`docker login`

#### Name of docker image to update/create
`IMAGE_NAME=tf_serving_bert_toxic`  

#### Version for docker image - NOTE to update a model this must get incremented
`VER=1557429385_v0.01`

#### Tensorflow Serving Model Name - NOTE this should always stay 'bert'
`MODEL_NAME=bert`

#### Put your docker user here
`DOCKER_USER=       {your docker user} `


#### GPU

```
cd ~
docker run -d --name $IMAGE_NAME labs12twitterblocker/tensorflow-serving-gpu:GPUv1
mkdir ~/models
```

#### CPU

```
cd ~
docker run -d --name $IMAGE_NAME labs12twitterblocker/tensorflow-serving:cpu3
mkdir ~/models
```



#### To use a different model change the path - NOTE this should point to a Saved_Model.pb and variables folder.
`gsutil cp -r  gs://not-another-bert-bucket/bert/export/multilabel/1557429385 ~/models`
##### Max Sequence Length 32:
`gsutil cp -r  gs://not-another-bert-bucket/bert/export/multilabel/1557439480 ~/models`
```
docker cp ~/models $IMAGE_NAME:/models/$MODEL_NAME
docker commit --change "ENV MODEL_NAME $MODEL_NAME" $IMAGE_NAME $DOCKER_USER/$IMAGE_NAME
docker tag $DOCKER_USER/$IMAGE_NAME $DOCKER_USER/$IMAGE_NAME:$VER
docker push $DOCKER_USER/$IMAGE_NAME:$VER
```
 
____

### 3. Create Container for Flask Client
#### (Run these commands in Google Cloud Services Console)
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

  
### 4. Deploy To Kubernetes/Google Cloud Services
  #### (Run these commands locally)
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


# Useful Commands





#Experimental
TF_SERVING_BUILD_OPTIONS="--copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-msse4.1 --copt=-msse4.2 --tensorflow_intra_op_parallelism=4 --tensorflow_inter_op_parallelism=4"
#Experimental

TF_SERVING_BUILD_OPTIONS="--copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-msse4.1 --copt=-msse4.2



# CREATE OPTIMIZED TF-SERVING CONTAINER
## CPU (RUN THIS LOCAL)

TF_SERVING_BUILD_OPTIONS="--copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-msse4.1 --copt=-msse4.2`

`git clone https://github.com/tensorflow/serving`

```
cd serving && \
  docker build --pull -t $DOCKER_USER/tensorflow-serving-devel:$VER \ 
  --build-arg TF_SERVING_BUILD_OPTIONS="${TF_SERVING_BUILD_OPTIONS}" \
  -f tensorflow_serving/tools/docker/Dockerfile.devel .

cd serving && \
  docker build -t $DOCKER_USER/tensorflow-serving:$VER \
  --build-arg TF_SERVING_BUILD_IMAGE=$DOCKER_USER/tensorflow-serving-devel:$VER \
-f tensorflow_serving/tools/docker/Dockerfile .
```

## GPU (RUN THIS LOCAL-NVIDIA GPU + DRIVERS + CUDA REQUIRED)

Google Cloud Hardware Optimizations
`TF_SERVING_BUILD_OPTIONS="--copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-msse4.1 --copt=-msse4.2"`

`git clone https://github.com/tensorflow/serving`

 `VER=GPUv1`
 
 `cd serving`

```
docker build --pull -t $DOCKER_USER/tensorflow-serving-devel-gpu:$VER --build-arg TF_SERVING_BUILD_OPTIONS="${TF_SERVING_BUILD_OPTIONS}" -f tensorflow_serving/tools/docker/Dockerfile.devel-gpu .
```

```
docker build -t $DOCKER_USER/tensorflow-serving-gpu:$VER --build-arg TF_SERVING_BUILD_IMAGE=$DOCKER_USER/tensorflow-serving-devel-gpu:$VER -f tensorflow_serving/tools/docker/Dockerfile.gpu .
```


# Debug


