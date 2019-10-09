# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 18:35:57 2019

@author: liyin
"""

import numpy as np
from analysis.prepare_data import distance_percentile2
from analysis.prepare_data import min_max_feature
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

percents= [0,30,70,100]
df['front_distances'] = df['ID'].apply(lambda id: distance_percentile2(id, 'F', percents))
# df['side_distances'] = df['ID'].apply(lambda id: distance_percentile2(id, 'S',percents))
# df['back_distances'] = df['ID'].apply(lambda id: distance_percentile2(id, 'B'))
s = df.apply(lambda x: pd.Series(x['front_distances']),axis=1)
cols = ['f1','f2','f3','f4','f5','f6','f7','f8']
df[cols]=s
for col in cols:
    df[col]=df[col]*df['身高']/df['fh']
df[cols]


df['side_distances'] = df['ID'].apply(lambda id: min_max_feature(id, 'S'))
scols = ['smin','smax']
ss = df.apply(lambda x: pd.Series(x['side_distances']),axis=1)
df[scols] = ss
for col in scols:
    df[col]=df[col]*df['身高']/df['fh']


# scols = ['s1','s2','s3','s4','s5','s6','s7','s8']
# ss = df.apply(lambda x: pd.Series(x['side_distances']),axis=1)
# df[scols] = ss
# for col in scols:
#     df[col]=df[col]*df['身高']/df['fh']

# bcols = ['b1','b2','b3','b4','b5','s6','s7','s8']

length = len(percents)
X1 = df[cols[:length]+['smax']].values
X2 = df[cols[length:]+['smin']].values

Y1=df['胸围'].values
Y2=df['腰围'].values
# Y = np.concatenate((y1.reshape(-1,1),y2.reshape(-1,1)),axis=1)
#
# np.save('X.npz',X)
# np.save('Y.npz',Y)
#
# X=np.load('X.npz.npy')
# Y=np.load('Y.npz.npy')

from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X1,Y1)
print(model.coef_,model.intercept_)
Y_pred=model.predict(X1)
diff=Y_pred-Y1
print(pd.Series(diff).describe())

import matplotlib.pyplot as plt
plt.hist(diff,bins=10)
plt.show()

from sklearn.externals import joblib
joblib.dump(value=model, filename=os.path.join(dir,'main_body_xiong.model'))

model2 = LinearRegression()
model2.fit(X2,Y2)
print(model2.coef_,model2.intercept_)
Y_pred=model2.predict(X2)
diff=Y_pred-Y2
print(pd.Series(diff).describe())

plt.hist(diff,bins=10)
plt.show()

joblib.dump(value=model2, filename=os.path.join(dir,'main_body_yao.model'))



