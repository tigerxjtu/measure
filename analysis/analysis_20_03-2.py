import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import warnings;

warnings.filterwarnings(action='once')

large = 22
med = 16
small = 12

params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")

mpl.rcParams['font.sans-serif'] = ['KaiTi']
mpl.rcParams['font.serif'] = ['KaiTi']


file=r'C:\projects\python\data\measure\202003\Data2.xls'
df=pd.read_excel(file,sheet_name=0)
df.index=df['数据库编号']

names=df['姓名'].unique().tolist()
cols=['颈围','肩宽','胸围','腰围','臀围']
cols1=[f'{col}A' for col in cols]
cols2=[f'{col}B' for col in cols]

df=df[['姓名']+cols2]
df_grouped=df.groupby('姓名')

df_mean=df_grouped.agg(np.mean)
df_max=df_grouped.agg(np.max)
df_min=df_grouped.agg(np.min)
df_diff=df_max-df_min

# diff_func=lambda x: x.max()-x.min()
# df_diff=df_grouped.transform(diff_func)
print(df_diff)
df_diff.to_excel(r'C:\projects\python\data\measure\202003\diff_0_side.xls')

# agg_dict={'均值':np.mean,'方差':np.std,'样本数':np.size}
# df_agg=df_grouped.agg(agg_dict)

df_agg=df_grouped.agg([np.mean,np.std,np.size])

abs(df_agg).to_excel(r'C:\projects\python\data\measure\202003\agg_0_side.xls')

from pandas.plotting import parallel_coordinates
plt.figure(figsize=(12, 9), dpi=80)
dft = abs(df_mean[cols])
dft['index']=df_mean.index
parallel_coordinates(dft, 'index', colormap='Dark2')
# Lighten borders
plt.gca().spines["top"].set_alpha(0)
plt.gca().spines["bottom"].set_alpha(.3)
plt.gca().spines["right"].set_alpha(0)
plt.gca().spines["left"].set_alpha(.3)
plt.title('误差比较', fontsize=22)
plt.grid(alpha=0.3)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.show()

def convert_cols_to_rows(df):
    d=abs(df).stack().reset_index()
    d=d[d.columns[-2:]]
    d.columns=['col','value']
    return d

df_grouped=df.groupby('姓名')

# Draw Plot
for name,group in df_grouped:
    plt.figure(figsize=(13,10), dpi= 80)
    dft = group[cols]
    dft=convert_cols_to_rows(dft)
    sns.boxplot(x='col', y='value', data=dft)
    sns.stripplot(x='col', y='value', data=dft, color='black', size=5, jitter=1)
    # Decoration
    plt.title(f'{name}尺寸箱线图', fontsize=22)
    plt.show()

# Draw Plot
for name in names:
    plt.figure(figsize=(13,10), dpi= 80)
    dft = df[df['姓名'] == name][cols1]
    dft=convert_cols_to_rows(dft)
    sns.boxplot(x='col', y='value', data=dft)
    sns.stripplot(x='col', y='value', data=dft, color='black', size=5, jitter=1)
    # Decoration
    plt.title(f'{name}正面特征尺寸箱线图', fontsize=22)
    plt.show()

# Draw Plot
for name in names:
    plt.figure(figsize=(13,10), dpi= 80)
    dft = df[df['姓名'] == name][cols2]
    dft=convert_cols_to_rows(dft)
    sns.boxplot(x='col', y='value', data=dft)
    sns.stripplot(x='col', y='value', data=dft, color='black', size=5, jitter=1)
    # Decoration
    plt.title(f'{name}侧面特征尺寸箱线图', fontsize=22)
    plt.show()