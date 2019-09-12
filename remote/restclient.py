
from Config import config
import requests

class RestClient(object):

    def __init__(self):
        self.url = config.httpInfo

    def post(self,data):
        response = requests.post(self.url, data=data)
        res = response.content.decode('unicode_escape')
        return res
    
    def update_status(self, id, status):
        post_data = {'OPT':21}
        post_data['BBI01'] = id
        post_data['status'] = status
        return self.post(post_data)

    # 查询特征点文件是否被修改过
    def get_feature_xy_status(self):
        post_data = {'askPassword': 'joypool2018', 'OPT': 22}
        return self.post(post_data)


