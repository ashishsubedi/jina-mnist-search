import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import pandas as pd

from jina import Document, Executor, Flow, requests
from jina.types.arrays.document import DocumentArray
from jina.types.document.generators import from_ndarray
from PIL import Image, ImageOps

from binascii import a2b_base64


X_train = pd.read_csv('./data/train.csv')
X_train = X_train.drop('label',axis =1)


encoder = None

def load_model():
    global encoder
    if encoder == None:
        encoder = tf.keras.models.load_model('./model/mnist_encoder_model.h5')
        print('Model loaded')
    return encoder


def mnist_encode_gen():
    size = 100
    for i in range(size):
        img = X_train.iloc[i].to_numpy(dtype='float32')
        img /= 255.0
        yield Document(embedding=encoder.predict(img.reshape(-1,28,28,1)),tags={'id':int(i)})

class MnistExecutor(Executor):
    _docs = DocumentArray()
    @requests(on='/index')
    def mnist_index(self,docs,**kwargs):
        self._docs.extend(docs)
        print("Indexing Complete...")
            
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

            query.matches = [Document(self._docs[int(idx)], copy=True,tags={'score':float(d[0]),'id': int(self._docs[int(idx)].tags['id'])}) for idx, d in enumerate(dist)]
            query.matches.sort(key=lambda m: m.tags['score'])
        
        return docs

        
        


f = Flow(port_expose=12345, protocol='http',cors=True).add(uses=MnistExecutor)
with f:
    encoder = load_model()
 
    f.post(on='/index',inputs=mnist_encode_gen)

    f.block()