import pandas as pd
from common import *
from train_data import *
from ui.Body import FrontBody,SideBody,BackBody
from utils import distance
import numpy as np
from BodyFeature import min_feature_range,max_feature_range

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

def xiong_distance(id,tag):
    body = get_body(id,tag)
    features = body.calculate_features()
    left,right = features['xiong_L'],features['xiong_R']
    return distance(left, right)

def yao_distance(id,tag):
    body = get_body(id,tag)
    features = body.calculate_features()
    left,right = features['yao_L'],features['yao_R']
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

def distance_percentile(id,tag):
    try:
        body = get_body(id, tag)
        body.calculate_features()
        distances = body.get_main_distances()
        # return distances
        return np.percentile(distances,[0,25,50,75,100])
    except Exception as e:
        print(id)
        # raise e

def main_body_distances(id,tag):
    try:
        body = get_body(id, tag)
        body.calculate_features()
        distances = body.get_main_distances()
        # return distances
        return distances
    except Exception as e:
        print(id)

def distance_percentile2(id,tag,percents=[0,25,50,75,100]):
    try:
        body = get_body(id, tag)
        body.calculate_features()
        distances_up, distances_down = body.get_main_distances2()
        # return distances
        up,down = np.percentile(distances_up,percents),np.percentile(distances_down,percents)
        return up.tolist()+down.tolist()
    except Exception as e:
        print(id)

def min_max_feature(id,tag):
    try:
        body = get_body(id, tag)
        body.calculate_features()
        lower_y, upper_y, _ = body.get_main_range()
        mid_y = int((upper_y+lower_y)/2)
        max_f=max_feature_range(body.outline,lower_y,mid_y)
        min_f = min_feature_range(body.outline, mid_y, upper_y)
        return min_f[2],max_f[2]
    except Exception as e:
        print(id)

def process_data_and_export(exclude_ids=None):
    df = load_dataset()
    # df.to_json(r'C:\projects\python\measure\ui\data\userinfo.json')
    df['has_feature'] = df['ID'].apply(feature_exists)
    df = df[df['has_feature'] == 1]

    if exclude_ids:
        df['notin']=df['ID'].apply(lambda id: id not in exclude_ids)
        df = df[df['notin']]

    df['front_neck'] = df['ID'].apply(lambda id: neck_distance(id, 'F'))
    df['side_neck'] = df['ID'].apply(lambda id: neck_distance(id, 'S'))
    df['back_neck'] = df['ID'].apply(lambda id: neck_distance(id, 'B'))

    df['front_shoulder'] = df['ID'].apply(lambda id: shoulder_distance(id, 'F'))
    df['back_shoulder'] = df['ID'].apply(lambda id: shoulder_distance(id, 'B'))

    df['front_hip'] = df['ID'].apply(lambda id: hip_distance(id, 'F'))
    df['side_hip'] = df['ID'].apply(lambda id: hip_distance(id, 'S'))
    df['back_hip'] = df['ID'].apply(lambda id: hip_distance(id, 'B'))

    df['front_xiong'] = df['ID'].apply(lambda id: xiong_distance(id, 'F'))
    df['side_xiong'] = df['ID'].apply(lambda id: xiong_distance(id, 'S'))
    df['back_xiong'] = df['ID'].apply(lambda id: xiong_distance(id, 'B'))

    df['front_yao'] = df['ID'].apply(lambda id: yao_distance(id, 'F'))
    df['side_yao'] = df['ID'].apply(lambda id: yao_distance(id, 'S'))
    df['back_yao'] = df['ID'].apply(lambda id: yao_distance(id, 'B'))

    df['fh'] = df['ID'].apply(front_height)
    df['sh'] = df['ID'].apply(side_height)
    df['bh'] = df['ID'].apply(back_height)

    df.to_excel(output_file_path)


if __name__ == '__main__':
    # ['U1002249190901112005186', 'U1002257190901114428127', 'U1002258190901114729512', 'U1002244190901110356672'] xiong,yao
    # ['U1002236190901103643327', 'U1002221190901094300643', 'U1002247190901111112451', 'U1002259190901114923542'] hip
    process_data_and_export()
    body_id = 'U1002260190901115100866'
    # user_info = build_user_info()
    # print(user_info)

    # distances = distance_percentile(body_id,'S')
    # print(distances)
    # distances = distance_percentile2(body_id, 'S')
    # print(distances)
    print(min_max_feature(body_id,'S'))

    # print(min(distances))
    # print(max(distances))
    # print(np.percentile(distances, [0, 25, 50, 75, 100]))





