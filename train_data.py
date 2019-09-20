from common import *
from BodyClient import body_client
import time

names=list_name(path1)
pics=list_pic_files(path2)
bd_path = r'C:\projects\python\measure\ui\data\bd'

#根据文件id和标签得到对应的特征文件和图片文件路径
def get_file_name(name,tag):
    file_name='%s%s1.txt'%(name,tag)
    pic_name='%s%s.jpg'%(name,tag)
    # print(file_name,pic_name,pics[pic_name])
    return os.path.join(path1,file_name),pics[pic_name]

def get_user_info(file_path):
    with open(file_path, encoding='UTF-8') as f:
        userdata = json.load(f)
        records = {}
        for ud in userdata:
            records[ud['id']]=ud
        return records

def save_feature(name):
    tags = ['F', 'S', 'B']
    for tag in tags:
        _, pic_file = get_file_name(name, tag)
        points, outline, rect = body_client.process_body(pic_file)
        out_file = '%s%s1.json' % (name, tag)
        with open(os.path.join(bd_path,out_file), 'w') as fp:
            json.dump(points, fp)
        out_file = '%s%s2.json' % (name, tag)
        with open(os.path.join(bd_path,out_file), 'w') as fp:
            json.dump(outline, fp)
        out_file = '%s%s3.json' % (name, tag)
        with open(os.path.join(bd_path,out_file), 'w') as fp:
            json.dump(rect, fp)

if __name__ == '__main__':
    print(names)
    # body = BodyFeature()
    # save_feature(names[0])
    # for name in names:
    #     try:
    #         save_feature(name)
    #         time.sleep(3)
    #     except Exception as e:
    #         print(name)
    #         print(e)
    print(path1)
    print(pics)
