import pandas as pd
from common import *
from train_data import *
from ui.Body import FrontBody,SideBody,BackBody
from utils import distance

data_file_path = r'C:\projects\python\measure\ui\data\201909模型数据.xlsx'
output_file_path = r'C:\projects\python\measure\ui\data\201909模型数据_out.xlsx'
def load_dataset():
    df = pd.read_excel(data_file_path)
    return df

def build_user_info():
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

def check_id(df):
    ids = df['ID'].values.tolist()
    for id in ids:
        if not id in names:
            print(id)

def get_body(id, tag):
    if tag=='F':
        body = FrontBody(id)
    elif tag == 'B':
        body = BackBody(id)
    else:
        body = SideBody(id)
    body.load_outline()
    body.load_pre_feature()
    return body

def shoulder_distance(id,tag):
    body = get_body(id,tag)
    left, right = body.process_shoulder_feature()
    return distance(left, right)

def neck_distance(id,tag):
    body = get_body(id, tag)
    left, right = body.proces_neck_feature()
    return distance(left, right)

def hip_distance(id,tag):
    body = get_body(id, tag)
    left,right = body.process_hip_feature()
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

def back_height(id):
    body = BackBody(id)
    body.load_outline()
    h = body._max_y - body._min_y
    return h

def feature_exists(id):
    file = os.path.join(path3,'%sF.json'%id)
    if os.path.exists(file):
        return 1
    else:
        return 0

if __name__ == '__main__':
    df = load_dataset()
    # df.to_json(r'C:\projects\python\measure\ui\data\userinfo.json')
    df['has_feature']=df['ID'].apply(feature_exists)
    df = df[df['has_feature']==1]

    df['front_neck']=df['ID'].apply(lambda id: neck_distance(id,'F'))
    df['side_neck']=df['ID'].apply(lambda id: neck_distance(id,'S'))
    df['back_neck'] = df['ID'].apply(lambda id: neck_distance(id, 'B'))

    df['front_shoulder']=df['ID'].apply(lambda id: shoulder_distance(id,'F'))
    df['back_shoulder'] = df['ID'].apply(lambda id: shoulder_distance(id, 'B'))

    df['front_hip'] = df['ID'].apply(lambda id: hip_distance(id, 'F'))
    df['side_hip'] = df['ID'].apply(lambda id: hip_distance(id, 'S'))
    df['back_hip'] = df['ID'].apply(lambda id: hip_distance(id, 'B'))

    df['fh']=df['ID'].apply(front_height)
    df['sh']=df['ID'].apply(side_height)
    df['bh'] = df['ID'].apply(back_height)

    df.to_excel(output_file_path)

    # user_info = build_user_info()
    # print(user_info)




