import json

class Config(object):

    def __init__(self):
        self.httpInfo = 'http://47.100.216.92/admin/app/index.html'


    def build_dict(self):
        conf = {}
        conf['httpInfo']= self.httpInfo
        return conf

    def read(self,file_path='config.json'):
        try:
            with open(file_path, 'r') as f:
                conf = json.loads(f.read())
                self.httpInfo = conf['httpInfo']
        except Exception as e:
            # print(e)
            pass

    def save(self,file_path='config.json'):
        conf = self.build_dict()
        with open(file_path, 'r') as f:
            json.dump(conf,f)


config = Config()
config.read()
