# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 18:35:57 2019

@author: liyin
"""

import numpy as np
from analysis.neck_data import output_file_path
from common import path3
import pandas as pd
import os

dir=r'C:\projects\python\measure\ui\data'
file_path = r'neck_output.xlsx'
df=pd.read_excel(os.path.join(dir,file_path))
df.columns
df['颈围'].describe()

neck_mean = 40

df['front']=df['front_neck']*df['身高']/df['fh']
df['front'].describe()

df['side']=df['side_neck']*df['身高']/df['sh']
df['side'].describe()

X=df[['front','side']]
df['front2']=X['front']*X['front']
df['side2']=X['side']*X['side']
df['front_side']=X['front']*X['side']
# df['front_side']=np.sqrt(X['front']*X['side'])

# X_train=df[['front2','side2','front_side']]
df['neck']=df['颈围']-neck_mean
Y=df['neck']

#X_train=df[['front','side','back']]
X_train=df[['front','side','front2','side2','front_side']]
# X_train=df[['front','side','front_side']]

# X_train=df[['front_back','side']]

#from sklearn.decomposition import PCA
#pca=PCA(n_components=2)
#X_train=pca.fit_transform(X_train)


from sklearn.linear_model import LinearRegression
model = LinearRegression()

model.fit(X_train,Y)
Y_pred=model.predict(X_train)
diff=Y_pred-Y

diff

diff.describe()

import matplotlib.pyplot as plt
plt.hist(diff,bins=8)
plt.show()

# diff.plot(kind='hist')


df['diff']=diff
df.to_excel(os.path.join(dir,'neck_output.xlsx'))

from sklearn.externals import joblib

joblib.dump(value=model, filename=os.path.join(dir,'neck.model'))

# df.to_excel(os.path.join(path3,'records.xlsx'))
#
# diff=np.abs(diff)
# #dir(diff)
# d=diff.to_numpy()
# d[np.where(d<1)]
#
# import matplotlib.pyplot as plt
# plt.figure(figsize=(16,9))
# data=df[['front','side','neck','front2','side2','front_side']]
# data.plot.scatter(x='front_side',y='neck')
