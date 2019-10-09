# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 18:35:57 2019

@author: liyin
"""

import numpy as np
from analysis.prepare_data import *
import pandas as pd
import os

dir=r'C:\projects\python\measure\ui\data'
file_path = r'201909模型数据_out.xlsx'
df=pd.read_excel(os.path.join(dir,file_path))
df.columns
df['胸围'].describe()
df['腰围'].describe()
xiong_mean = 95
yao_mean = 84

df['front_distances'] = df['ID'].apply(lambda id: distance_percentile(id, 'F'))
df['side_distances'] = df['ID'].apply(lambda id: distance_percentile(id, 'S'))
s = df.apply(lambda x: pd.Series(x['front_distances']),axis=1)
cols = ['f1','f2','f3','f4','f5']
df[cols]=s
for col in cols:
    df[col]=df[col]*df['身高']/df['fh']
df[cols]

scols = ['s1','s2','s3','s4','s5']
ss = df.apply(lambda x: pd.Series(x['side_distances']),axis=1)
df[scols] = ss
for col in scols:
    df[col]=df[col]*df['身高']/df['fh']

X = df[cols+scols].values

y1=df['胸围'].values
y2=df['腰围'].values
Y = np.concatenate((y1.reshape(-1,1),y2.reshape(-1,1)),axis=1)

np.save('X.npz',X)
np.save('Y.npz',Y)

X=np.load('X.npz.npy')
Y=np.load('Y.npz.npy')

from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X,Y)
Y_pred=model.predict(X)
diff=Y_pred-Y

import matplotlib.pyplot as plt
plt.hist(diff[:,0],bins=8)
plt.show()
plt.hist(diff[:,1],bins=8)
plt.show()

from sklearn.externals import joblib
joblib.dump(value=model, filename=os.path.join(dir,'main_body.model'))



