# Elastic Synapse Processor
![img](https://i.imgur.com/VfvCPuH.jpg)

____

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
  
  





