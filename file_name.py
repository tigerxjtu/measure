import importlib
from Config import config
import os

file_module = None
if config.train_mode:
    file_module = importlib.import_module('train_data')


def get_file_name_db(name,tag,*args):
    folder = args[0]
    feature_path = os.path.join(config.txt_dir,folder)
    pic_path = os.path.join(config.pic_dir,folder)
    return os.path.join(feature_path,'%s%s1.txt'%(name,tag)),os.path.join(pic_path,'%s%s.jpg'%(name,tag))

global get_file_name
if file_module:
    # print(dir(file_module))
    get_file_name=file_module.get_file_name
else:
    get_file_name = get_file_name_db