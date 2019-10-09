import keras
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential  #顺序模型
from keras.layers import Dense #全连接层

x_data = np.load('X.npz.npy')
y_data = np.load('Y.npz.npy')
y_data = y_data[:,1]

model=Sequential()
# 1-1
# model.add(Dense(units=1,input_dim=1)) #一个输出，一个输入

#1-10-1
model.add(Dense(units=20,input_dim=10,activation='tanh'))
# model.add(keras.layers.Activation('tanh'))
model.add(Dense(units=1,activation='tanh'))
# model.add(keras.layers.Activation('tanh'))
model.compile(optimizer=keras.optimizers.SGD(lr=0.3),loss=keras.losses.mse)

for step in range(30000):
    cost=model.train_on_batch(x_data,y_data)
    if step % 500 ==0:
        print('cost:',cost)

# W,b=model.layers[0].get_weights()
# print('W:',W,'b:',b)
model.save('main_body.h5')

y_pred=model.predict(x_data)
diff = y_pred - y_data
plt.hist(diff[:,0],bins=8)
plt.show()
plt.hist(diff[:,1],bins=8)
plt.show()