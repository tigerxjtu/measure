import json
import os

# path1=r'C:\projects\python\measure\ui\data\txtdata'
# path2=r'C:\projects\python\measure\ui\data\pics'

path1=r'data\txtdata'
path2=r'data\pics'
path3=r'data\result'

#获取文件名的ID含义部分
def get_name(file_name):
    return file_name[:-6]

#遍历文件得到所有id列表
def list_name(path):
    names={}
    for file_name in os.listdir(path):
        names[get_name(file_name)]=1
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

names=list_name(path1)
pics=list_pic_files(path2)

#根据文件id和标签得到对应的特征文件和图片文件路径
def get_file_name(name,tag):
    file_name='%s%s1.txt'%(name,tag)
    pic_name='%s%s.jpg'%(name,tag)
    # print(file_name,pic_name,pics[pic_name])
    return os.path.join(path1,file_name),pics[pic_name]


if __name__ == '__main__':
    print(names)