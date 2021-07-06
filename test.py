# import numpy as np

# q = np.random.randn(2, 1, 30)

# d = np.random.randn(100, 1, 30)

# d_norm = np.linalg.norm(d,axis=2)

# # print(d_norm)
# print(d_norm.shape)

# q_norm = np.linalg.norm(q,axis=2)

# # print(q_norm)
# print(q_norm.shape)
# res = q_norm * d_norm
# # print(res)
# print(res.shape)

# q_prime = np.swapaxes(q,1,2)
# # print(q_prime)
# print(q_prime.shape)

# dot = d.dot(q_prime)
# # print(dot)
# dot = dot.reshape((100,1))
# print(dot.shape)
# # print(dot)

# print(dot/res)

# def cosine_similarity(q, d):
#     d_norm = np.linalg.norm(d,axis=2)
#     q_norm = np.linalg.norm(q,axis=2)

#     deno = q_norm * d_norm
#     q_prime = np.swapaxes(q,1,2)

#     dot = d.dot(q_prime)
#     dot = dot.reshape((100,1))

#     return (dot/(deno + 1e-5))



import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('./data/train_sample.csv')
print(df.iloc[85,0])