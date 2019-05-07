# Elastic Synapse Processor
  ### Pre-Requisites:
  * Google Cloud Services Account
  * Google Cloud Bucket
  * Dockerhub Account
  



## Model Training and Deployment Pipeline

### 1. Model Training: 
  https://colab.research.google.com/drive/1X2zP-C3os4vt0jlJ_OQ_u5kq6pGErPd3
  #### TODO : ADD FURTHER DETAILS/INSTRUCTION
  
### 2. Create Container For Model
  #### Run these commands in Google Cloud Services Console
`
IMAGE_NAME=tf_serving_bert_toxic

VER=1556822021_v5

MODEL_NAME=bert

DOCKER_USER=chrisseiler96

cd ~

docker run -d --name $IMAGE_NAME tensorflow/serving

mkdir ~/models

gsutil cp -r  gs://not-another-bert-bucket/bert/export/multilabel/1556822021 ~/models

docker cp ~/models $IMAGE_NAME:/models/$MODEL_NAME

docker commit --change "ENV MODEL_NAME $MODEL_NAME" $IMAGE_NAME $USER/$IMAGE_NAME

docker tag $USER/$IMAGE_NAME $DOCKER_USER/$IMAGE_NAME:$VER

docker push $DOCKER_USER/$IMAGE_NAME:$VER
`
  
  
### 3. Create Container for Flask Client
  #### TODO: ADD FURTHER DETAILS/INSTRUCTION
  
  
### 4. Deploy To Kubernetes/Google Cloud Services
  #### TODO: ADD FURTHER DETAILS/INSTRUCTION
  





