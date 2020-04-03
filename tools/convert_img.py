import os
import cv2

def list_filename(path):
    names={}
    for file_name in os.listdir(path):
        if os.path.isdir(file_name):
            continue
        names[file_name]=os.path.join(path,file_name)
    return names

def convert_imgs(src_path,dst_path):
    names=list_filename(src_path)
    for filename,filepath in names.items():
        img=cv2.imread(filepath)
        h,w=img.shape[:2]
        img=cv2.resize(img,(w//2,h//2))
        path=os.path.join(dst_path,filename)
        cv2.imwrite(path,img)

if __name__ == '__main__':
    src_path=r'C:\projects\python\data\measure\YS20200318A'
    dst_path=r'C:\projects\python\data\measure\output'
    convert_imgs(src_path,dst_path)