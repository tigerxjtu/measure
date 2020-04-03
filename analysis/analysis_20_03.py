import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import warnings;

warnings.filterwarnings(action='once')

large = 22;
med = 16;
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

file=r'C:\projects\python\data\measure\202003\Data.xls'
df=pd.read_excel(file)
df1=df[df['姓名']=='徐平显']
df2=df[df['姓名']=='孙溪']
names=['徐平显','孙溪']
cols=['颈围','肩宽','胸围','腰围','臀围']

dd=df1[cols]

dd1=dd.stack()
dd1.reset_index()
dd2=dd1.reset_index()

def convert_cols_to_rows(df):
    d=abs(df).stack().reset_index()
    d=d[d.columns[-2:]]
    d.columns=['col','value']
    return d

print(convert_cols_to_rows(dd))
# d = pd.read_csv("C:\工作\good\python\datasets\mpg_ggplot2.csv")
#
# d[['class','hwy']]
# # Draw Plot
# plt.figure(figsize=(13,10), dpi= 80)
# sns.violinplot(x='class', y='hwy', data=d, scale='width', inner='quartile')
# # Decoration
# plt.title('Violin Plot of Highway Mileage by Vehicle Class', fontsize=22)
# plt.show()

# dft=convert_cols_to_rows(df1[cols])
# sns.violinplot(x='col', y='value', data=dft, scale='width', inner='quartile')
# # Decoration
# name='徐平显'
# plt.title(f'{name}的测量尺寸分布图', fontsize=22)
# plt.show()

for name in names:
    plt.figure(figsize=(13, 10), dpi=80)
    dft=df[df['姓名']==name][cols]
    dft=convert_cols_to_rows(dft)
    sns.violinplot(x='col', y='value', data=dft, scale='width', inner='quartile')
    # Decoration
    plt.title(f'{name}的测量尺寸分布图', fontsize=22)
    plt.show()

cols1=[f'{col}A' for col in cols]
for name in names:
    plt.figure(figsize=(13, 10), dpi=80)
    dft=df[df['姓名']==name][cols1]
    dft=convert_cols_to_rows(dft)
    sns.violinplot(x='col', y='value', data=dft, scale='width', inner='quartile')
    # Decoration
    plt.title(f'{name}的正面特征尺寸分布图', fontsize=22)
    plt.show()


cols2=[f'{col}B' for col in cols]
for name in names:
    plt.figure(figsize=(13, 10), dpi=80)
    dft=df[df['姓名']==name][cols2]
    dft=convert_cols_to_rows(dft)
    sns.violinplot(x='col', y='value', data=dft, scale='width', inner='quartile')
    # Decoration
    plt.title(f'{name}的侧面特征尺寸分布图', fontsize=22)
    plt.show()

# Draw Plot
for name in names:
    plt.figure(figsize=(13,10), dpi= 80)
    dft = df[df['姓名'] == name][cols]
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

from pandas.plotting import parallel_coordinates
df_final = pd.read_csv("C:\工作\good\python\datasets\diamonds_filter.csv")
plt.figure(figsize=(12,9), dpi= 80)
parallel_coordinates(df_final, 'cut', colormap='Dark2')
# Lighten borders
plt.gca().spines["top"].set_alpha(0)
plt.gca().spines["bottom"].set_alpha(.3)
plt.gca().spines["right"].set_alpha(0)
plt.gca().spines["left"].set_alpha(.3)
plt.title('Parallel Coordinated of Diamonds', fontsize=22)
plt.grid(alpha=0.3)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.show()

df.index=df['数据库编号']

for name in names:
    plt.figure(figsize=(12, 9), dpi=80)
    dft = abs(df[df['姓名'] == name][cols])
    dft['index']=dft.index
    parallel_coordinates(dft, 'index', colormap='Dark2')
    # Lighten borders
    plt.gca().spines["top"].set_alpha(0)
    plt.gca().spines["bottom"].set_alpha(.3)
    plt.gca().spines["right"].set_alpha(0)
    plt.gca().spines["left"].set_alpha(.3)
    plt.title(f'{name}各部位误差比较', fontsize=22)
    plt.grid(alpha=0.3)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.show()

