import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import pandas as pd

from jina import Document, Executor, Flow, requests
from jina.types.arrays.document import DocumentArray
from jina.types.document.generators import from_ndarray
from PIL import Image, ImageOps

from binascii import a2b_base64

# from tensorflow.keras.applications.vgg16 import VGG16


X_train = pd.read_csv('./data/train.csv')
X_train = X_train.drop('label',axis =1)


encoder = None

def load_model():
    global encoder
    if encoder == None:
        # encoder = tf.keras.models.load_model('./model/mnist_encoder_model.h5')
        encoder = tf.keras.models.load_model('./model/mnist_dense_softmax.h5')
        print('Model loaded')
    return encoder


def mnist_encode_gen():
    size = 1000
    for i in range(size):
        img = X_train.iloc[i].to_numpy(dtype='float32')
        img /= 255.0
        yield Document(embedding=encoder.predict(img.reshape(-1,28,28)),tags={'id':int(i)})

def cosine_similarity(q, d):
    d_norm = np.linalg.norm(d,axis=2)
    q_norm = np.linalg.norm(q,axis=2)

    deno = q_norm * d_norm
    q_prime = np.swapaxes(q,1,2)

    dot = d.dot(q_prime)
    dot = dot.reshape((d.shape[0],1))

    return (dot/(deno + 1e-5))


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
        
        
        docs = DocumentArray([Document(embedding=encoder.predict(img.reshape(1,28,28)))])
    
        
        q = np.stack(docs.get_attributes('embedding'))
        d = np.stack(self._docs.get_attributes('embedding'))
        # print(q.shape,d.shape)
        eucledian_dist = np.linalg.norm(q[:, None, :] - d[None, :, :], axis=-1)
        # similarity = cosine_similarity(q,d)
        # similarity = similarity.reshape((1,similarity.shape[0],similarity.shape[1]))
        
        top_k = int(parameters['top_k']) if 'top_k' in parameters else 3
        for dist,query in zip(eucledian_dist,docs):

            query.matches = [Document(self._docs[int(idx)], copy=True,tags={'score':float(d[0]),'id': int(self._docs[int(idx)].tags['id'])}) for idx, d in enumerate(dist)]
            query.matches.sort(key=lambda m: m.tags['score'])

            if top_k < len(query.matches):
                query.matches = query.matches[:top_k]
                # print(query.matches)


        return docs
        
        


f = Flow(port_expose=12345, protocol='http',cors=True).add(uses=MnistExecutor)
with f:
    encoder = load_model()
 
    f.post(on='/index',inputs=mnist_encode_gen)

    f.block()