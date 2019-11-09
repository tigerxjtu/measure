import pandas as pd
from common import *
from train_data import names
from ui.Body import FrontBody,SideBody
from utils import distance
import os
from Config import config
import re

# data_file_path = r'C:\projects\python\measure\ui\data\201909模型数据.xlsx'
# output_file_path = r'C:\projects\python\measure\ui\data\201909模型数据_out.xlsx'
data_file_path = os.path.join(config.data_dir,'data.xlsx')
output_file_path = os.path.join(config.data_dir,'data_out.xlsx')

def load_dataset():
    df = pd.read_excel(data_file_path)
    return df

def build_user_info():
    try:
        df = load_dataset()
        result= {}
        df = df[['ID','身高','体重','颈围','胸围','腰围','臀围','肩宽']]
        data = df.values
        rows,cols = data.shape
        col_names = ['id','height','weight','neck','xiong','yao','tun','shoulder']
        result = {}
        for i in range(rows):
            record = {}
            for j in range(cols):
                record[col_names[j]] = data[i,j]
            result[record['id']]=record
        return result
    except Exception as e:
        print(e)
        return {}


def check_id(df):
    ids = df['ID'].values.tolist()
    for id in ids:
        if not id in names:
            print(id)

def shoulder_distance(id):
    body = FrontBody(id)
    body.load_feature()
    left,right = body.features['f_shoulder_L'],body.features['f_shoulder_R']
    return distance(left, right)

def front_distance(id):
    body = FrontBody(id)
    body.load_feature()
    # print(body.features)
    left, right = body.features['neck_left_L'], body.features['neck_left_R']
    return distance(left, right)

def side_distance(id):
    body = SideBody(id)
    body.load_feature()
    left, right = body.features['neck_left_L'], body.features['neck_left_R']
    return distance(left, right)

def front_height(id):
    body = FrontBody(id)
    body.load_feature()
    h = body.bottom_y - body.top_head_point[1]
    return h

def side_height(id):
    body = SideBody(id)
    body.load_feature()
    # print(id)
    h = body.bottom_y - body.top_head_point[1]
    return h


def feature_exists(id):
    file = os.path.join(path3,'%sF.json'%id)
    if os.path.exists(file):
        return 1
    else:
        return 0

def read_data(file_name):
    file = os.path.join(config.data_dir,file_name)
    df = pd.read_excel(file,header=0)
    result = {}
    for index, row in df.iterrows():
        record = {}
        key = row['name']
        record['neck']=row['neck']
        record['shoulder'] = row['shoulder']
        record['xiong'] = row['xiong']
        record['yao'] = row['yao']
        record['tun'] = row['tun']
        result[key]=record
    return result

def parse_file(file):
    parts = re.split('[/\\\\]',file)
    name = parts[-1][:-5]
    return name

def map_key_col(key,col,users):
    record = users[key]
    return record[col]

'''
SELECT
  b.id,
  BBI02 NAME,
  b.BBI03 height,
  b.BBI04 weight,
  p.bfd08 neck,
  p.bh11 shoulder,
  p.bfd11 xiong,
  p.bfd12 yao,
  p.bfd13 tun,
  f.bpf01 pic
FROM
  none_body_baseinfo b,
  none_body_feature_data p,
  none_body_picfile f
WHERE p.bbiid = b.id AND f.bbiid=b.id
  AND b.id>=1002396
ORDER BY b.bbi02
'''
def save_dataset():
    file = os.path.join(config.data_dir, 'records.csv')
    df = pd.read_csv(file,header=0,encoding='utf-8')
    print(df)
    df['ID']=df['pic'].apply(parse_file)
    cols=['ID', '身高', '体重', '颈围', '胸围', '腰围', '臀围', '肩宽']
    df['身高']=df['height']
    df['体重'] = df['weight']

    users = read_data('user.xlsx')

    df['颈围'] = df['NAME'].apply(lambda x:map_key_col(x,'neck',users))
    df['胸围'] = df['NAME'].apply(lambda x:map_key_col(x,'xiong',users))
    df['腰围'] = df['NAME'].apply(lambda x:map_key_col(x,'yao',users))
    df['臀围'] = df['NAME'].apply(lambda x:map_key_col(x,'tun',users))
    df['肩宽'] = df['NAME'].apply(lambda x:map_key_col(x,'shoulder',users))
    df =df[cols]
    df.to_excel(data_file_path)



if __name__ == '__main__':
    # df = load_dataset()
    # df.to_json(r'C:\projects\python\measure\ui\data\userinfo.json')
    # df['has_feature']=df['ID'].apply(feature_exists)
    # df = df[df['has_feature']==1]
    #
    # df['front_neck']=df['ID'].apply(front_distance)
    # df['side_neck']=df['ID'].apply(side_distance)
    #
    # df['shoulder']=df['ID'].apply(shoulder_distance)
    #
    # df['fh']=df['ID'].apply(front_height)
    # df['sh']=df['ID'].apply(side_height)
    #
    # df.to_excel(output_file_path)
    #
    # # user_info = build_user_info()
    # # print(user_info)

    save_dataset()





