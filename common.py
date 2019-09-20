import json
import os
from Config import config

# base_path = r'C:\projects\python\measure\ui\data'
# path1=r'C:\projects\python\measure\ui\data\txtdata'
# path2=r'C:\projects\python\measure\ui\data\pics'
# path3=r'C:\projects\python\measure\ui\data\result'

# path1=r'data\txtdata'
# path2=r'data\pics'
# path3=r'data\result'

base_path = config.model_path
path1=config.txt_dir
path2=config.pic_dir
path3=config.result_dir

#获取文件名的ID含义部分
def get_name(file_name):
    return file_name[:-6]

#遍历文件得到所有id列表
def list_name(path):
    names={}
    for file_name in os.listdir(path):
        if os.path.isdir(file_name):
            continue
        if not file_name.endswith('.txt'):
            continue
        name = get_name(file_name)
        if name:
            names[name]=1
    return [key for key in names.keys()]

#获取所有图片文件id、文件路径 pair
def list_pic_files(path):
    file_names={}
    for root,dirs,files in os.walk(path):
        for name in files:
            file_names[name]=os.path.join(root,name)
    return file_names

#获取特征文件对应的轮廓点或特征点
def get_points(file):
    with open(file) as f:
        content = f.read()
        data = json.loads(content)
        points = data['featureXY']
        return [(int(p['x']), int(p['y'])) for p in points]

# names=list_name(path1)
# pics=list_pic_files(path2)



