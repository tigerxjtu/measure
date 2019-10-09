import requests
import os
from Config import config
import json

headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

fixed_folder=True

def downloadFile(url,file_path):
    if url:
        response=requests.get(url,headers=headers)
        filename=url.split('/')[-1]
        path=os.path.join(file_path,filename)
        with open(path,'wb') as f:
            f.write(response.content)

def get_download_files(folder, body_id, status):
    pic_front = '%s/%s/%s'%(config.download_base_pic_url,folder,'%sF.jpg'%body_id)
    pic_side = '%s/%s/%s'%(config.download_base_pic_url,folder,'%sS.jpg'%body_id)
    pic_back = '%s/%s/%s'%(config.download_base_pic_url, folder, '%sB.jpg' % body_id)
    pic_files = [pic_front,pic_side,pic_back]
    tan_front = '%s/%s/%s' % (config.download_base_tan_url, folder, '%s_FC.txt' % body_id)
    tan_side = '%s/%s/%s' % (config.download_base_tan_url, folder, '%s_SC.txt' % body_id)
    tan_feature = '%s/%s/%s' % (config.download_base_tan_url, folder, '%s_FL.txt' % body_id)
    tan_files = []
    if status == 0:
        tan_files = [tan_front,tan_side,tan_feature]
    if status ==-1:
        tan_files = [tan_feature]
    if status ==-2:
        tan_files = [tan_front,tan_side]
    return pic_files, tan_files

def download_files(folder,body_id,status):
    pic_urls, tan_urls = get_download_files(folder,body_id,status)

    if not fixed_folder:
        pic_path = os.path.join(config.pic_dir,folder)
    else:
        pic_path = config.pic_dir
    if not os.path.exists(pic_path):
        os.mkdir(pic_path)

    if not fixed_folder:
        tan_path = os.path.join(config.tan_dir,folder)
    else:
        tan_path = config.tan_dir
    if not os.path.exists(tan_path):
        os.mkdir(tan_path)

    for url in pic_urls:
        downloadFile(url, pic_path)
    for url in tan_urls:
        downloadFile(url,tan_path)

def save_person_info(folder,person_info):
    if not fixed_folder:
        tan_path = os.path.join(config.tan_dir, folder)
    else:
        tan_path = config.tan_dir
    if not os.path.exists(tan_path):
        os.mkdir(tan_path)
    path = os.path.join(tan_path,'%s.txt'%person_info['body_id'])
    with open(path,'w') as f:
        # json.dump(person_info,f)
        for key,value in person_info.items():
            f.write('%s:%s\n'%(key,value))

#
# def downloadImg(url):
#     if url:
#         response=requests.get(url,headers=headers)
#         filename=url.split('/')[-1]
#         path=os.path.join(makedir('images'),filename)
#         f=open(path,'wb')
#         f.write(response.content)
#         f.close()