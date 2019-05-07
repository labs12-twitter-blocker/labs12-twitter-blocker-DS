
import grpc
import tensorflow as tf

#import run_multilabels_classifier as classifiers


from run_multilabels_classifier import MultiLabelTextProcessor 
from run_multilabels_classifier import convert_single_example 
from run_multilabels_classifier import create_int_feature


import tokenization
import collections

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from tensorflow.core.framework import tensor_pb2
from tensorflow.core.framework import tensor_shape_pb2
from tensorflow.core.framework import types_pb2


import numpy as np

from flask import Flask
from flask import request

import logging

import random

app = Flask(__name__)


@app.route("/", methods = ['GET'])
def hello():
  return "Hello BERT predicting Toxic Comments! Try posting a string to this url"


@app.route("/", methods = ['POST'])
def predict():
  # MODEL PARAMS
  max_seq_length = 128

  channel = grpc.insecure_channel("localhost:8500")
  stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

  # Parse Description
  tokenizer = tokenization.FullTokenizer(
    vocab_file="asset/vocab.txt", do_lower_case=True)
  processor = MultiLabelTextProcessor()
  label_list = [0,0,0,0,0,0]




  # logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
  # logger = logging.getLogger(__name__)
  # logger.info('getting json')
  content = request.get_json()
  #logger.info('JSON: {}'.format(content))
  request_id = str(random.randint(1, 9223372036854775807))


  inputExample = processor.serving_create_example([request_id, content['description']], 'test')
  feature = convert_single_example(0, inputExample, label_list, max_seq_length, tokenizer)
  
  features = collections.OrderedDict()
  features["input_ids"] = create_int_feature(feature.input_ids)
  features["input_mask"] = create_int_feature(feature.input_mask)
  features["segment_ids"] = create_int_feature(feature.segment_ids)
  features["is_real_example"] = create_int_feature([int(feature.is_real_example)])
  if isinstance(feature.label_id, list):
    label_ids = feature.label_id
  else:
    label_ids = [feature.label_id]
  features["label_ids"] = create_int_feature(label_ids)

  tf_example = tf.train.Example(features=tf.train.Features(feature=features))
  
  
  model_input = tf_example.SerializeToString()

  # Send request
  # See prediction_service.proto for gRPC request/response details.
  model_request = predict_pb2.PredictRequest()
  model_request.model_spec.name = 'bert'
  model_request.model_spec.signature_name = 'serving_default'
  dims = [tensor_shape_pb2.TensorShapeProto.Dim(size=1)]
  tensor_shape_proto = tensor_shape_pb2.TensorShapeProto(dim=dims)
  tensor_proto = tensor_pb2.TensorProto(
    dtype=types_pb2.DT_STRING,
    tensor_shape=tensor_shape_proto,
    string_val=[model_input])

  model_request.inputs['examples'].CopyFrom(tensor_proto)
  result = stub.Predict(model_request, 10.0)  # 10 secs timeout
  predict_response_dict = predict_response_to_dict(result)
  keys = [k for k in predict_response_dict]


  label_dict={'toxic':predict_response_dict['probabilities'][0][0],
            'severe_toxic':predict_response_dict['probabilities'][0][1] ,
            'obscene':predict_response_dict['probabilities'][0][2],
            'threat':predict_response_dict['probabilities'][0][3],
            'insult':predict_response_dict['probabilities'][0][4],
            'identity_hate':predict_response_dict['probabilities'][0][5]}



  pretty_result = "Prediction{}: "
  pretty_result = pretty_result.format(label_dict)
  #app.logger.info("Predicted Label: %s", label_list[result[0]])
  return pretty_result





dtype_to_number = {
    'DT_INVALID': 0,
    'DT_FLOAT': 1,
    'DT_DOUBLE': 2,
    'DT_INT32': 3,
    'DT_UINT8': 4,
    'DT_INT16': 5,
    'DT_INT8': 6,
    'DT_STRING': 7,
    'DT_COMPLEX64': 8,
    'DT_INT64': 9,
    'DT_BOOL': 10,
    'DT_QINT8': 11,
    'DT_QUINT8': 12,
    'DT_QINT32': 13,
    'DT_BFLOAT16': 14,
    'DT_QINT16': 15,
    'DT_QUINT16': 16,
    'DT_UINT16': 17,
    'DT_COMPLEX128': 18,
    'DT_HALF': 19,
    'DT_RESOURCE': 20
}



number_to_dtype_value = {
    1: 'float_val',
    2: 'double_val',
    3: 'int_val',
    4: 'int_val',
    5: 'int_val',
    6: 'int_val',
    7: 'string_val',
    8: 'scomplex_val',
    9: 'int64_val',
    10: 'bool_val',
    18: 'dcomplex_val',
    19: 'half_val',
    20: 'resource_handle_val'
}








def predict_response_to_dict(predict_response):
    predict_response_dict = dict()

    for k in predict_response.outputs:
        shape = [x.size for x in predict_response.outputs[k].tensor_shape.dim]

        #logger.debug('Key: ' + k + ', shape: ' + str(shape))

        dtype_constant = predict_response.outputs[k].dtype

        if dtype_constant not in number_to_dtype_value:
            #logger.error('Tensor output data type not supported. Returning empty dict.')
            predict_response_dict[k] = 'value not found'

        if shape == [1]:
            predict_response_dict[k] = eval('predict_response.outputs[k].' + number_to_dtype_value[dtype_constant])[0]
        else:
            predict_response_dict[k] = np.array(
                eval('predict_response.outputs[k].' + number_to_dtype_value[dtype_constant])).reshape(shape)

    return predict_response_dict





if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
