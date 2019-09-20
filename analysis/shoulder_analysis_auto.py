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
file_path = r'201909模型数据_out.xlsx'
df=pd.read_excel(os.path.join(dir,file_path))
df.columns
df['肩宽'].describe()

shoulder_mean = 42

df['front']=df['front_shoulder']*df['身高']/df['fh']
df['front'].describe()

df['back']=df['back_shoulder']*df['身高']/df['fh']
df['back'].describe()


X=df[['front','back']]

Y=df['肩宽']-shoulder_mean

#X_train=df[['front','side','back']]
X_train=X


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
df.to_excel(os.path.join(dir,'shoulder_output.xlsx'))

from sklearn.externals import joblib

joblib.dump(value=model, filename=os.path.join(dir,'shoulder.model'))

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
