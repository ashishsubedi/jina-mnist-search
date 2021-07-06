import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from jina import Document, Executor, Flow, requests
from jina.types.arrays.document import DocumentArray
from jina.types.document.generators import from_ndarray
from PIL import Image, ImageOps
# import jina.helper
from binascii import a2b_base64

from tensorflow.keras.datasets import mnist

(X_train,y_train),(X_test,y_test)=mnist.load_data()
X_train = np.expand_dims(X_train, axis=-1)
X_test = np.expand_dims(X_test, axis=-1)
X_train = X_train.astype("float32") / 255.0
X_test = X_test.astype("float32") / 255.0

encoder = None

def load_model():
    global encoder
    if encoder == None:
        encoder = tf.keras.models.load_model('./model/mnist_encoder_model.h5')
        print('Model loaded')
    return encoder

# print("Model Loaded:",encoder.summary())

def mnist_encode_gen():
    size = 100
    for i in range(size):
        yield Document(embedding=encoder.predict(X_test.reshape(-1,28,28,1)))

class MnistExecutor(Executor):
    _docs = DocumentArray()

    @requests(on='/index')
    def mnist_index(self,docs,**kwargs):
        self._docs.extend(docs)
        print("Indexing Done")
            
    @requests(on='/search')
    def mnist_search(self,parameters,**kwargs):
        binary_data = a2b_base64(parameters['image_uri'])
        # print(binary_data)
        fd = open('./temp.png', 'wb')
        fd.write(binary_data)
        fd.close()
        img = Image.open('./temp.png')
        img = ImageOps.grayscale(img)
        
        img = img.resize((28,28))
        img = np.asarray( img )
        img = img/255.0
       
        encoder = load_model()
        
        docs = DocumentArray([Document(embedding=encoder.predict(img.reshape(1,28,28,1)))])
       
        
        q = np.stack(docs.get_attributes('embedding'))
        d = np.stack(self._docs.get_attributes('embedding'))
        eucledian_dist = np.linalg.norm(q[:, None, :] - d[None, :, :], axis=-1)
        
        for dist,query in zip(eucledian_dist,docs):

            query.matches = [Document(self._docs[int(idx)], copy=True,tags={'score':float(d[0])}) for idx, d in enumerate(dist)]
            query.matches.sort(key=lambda m: m.tags['score'])
        
        
        return docs

        
        


# def extend_rest_function(app):


#     @app.get('/', tags=['Homepage Route'])
#     async def foo():
#         return "Hello World"

#     return app


# jina.helper.extend_rest_interface = extend_rest_function
f = Flow(port_expose=12345, protocol='http',cors=True).add(uses=MnistExecutor)

with f:
    encoder = load_model()
    f.post(on='/index',inputs=[Document(embedding=encoder.predict(X.reshape(-1,28,28,1))) for X in X_train[:100]])
    # f.post(on='/search',parameters={'image_uri': '/home/ash/Desktop/0.png'})
    f.block()